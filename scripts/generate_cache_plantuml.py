"""
Script de génération de diagrammes de cache avec PlantUML.

Génère des diagrammes de flux montrant le processus de cache multi-niveaux
pour la récupération de la liste des appareils Alexa.

Prérequis:
    Aucun (génère des fichiers .puml lisibles en texte)

Usage:
    python scripts/generate_cache_plantuml.py

Sortie:
    docs/diagrams/*.puml
    
Pour générer les images:
    - Utiliser l'extension VS Code PlantUML
    - Ou: java -jar plantuml.jar docs/diagrams/*.puml
"""

from pathlib import Path


def generate_cache_flow_puml():
    """Génère le diagramme de flux du système de cache en PlantUML."""
    
    content = """@startuml cache_flow_diagram
!theme plain
skinparam backgroundColor white
skinparam defaultFontSize 12
skinparam rectangleFontSize 14
skinparam noteFontSize 11

title Système de Cache Multi-Niveaux - Device List

actor "Utilisateur" as user
participant "CLI\\nalexa device list" as cli #LightBlue
participant "DeviceManager\\nget_devices()" as dm #LightGreen
participant "Cache Mémoire\\n(RAM)\\nTTL: 5 min" as mem #Yellow
participant "CacheService\\nget(ignore_ttl=True)" as cs #Orange
participant "Cache Disque\\n(devices.json.gz)\\nTTL: ∞ AUCUN" as disk #LightCoral
participant "Amazon API\\nalexa.amazon.com" as api #Red

== Scénario 1: Cache Mémoire Valide ==
user -> cli: alexa device list
cli -> dm: get_devices()
dm -> mem: Vérifier TTL
mem -> mem: ✅ TTL < 5 min
note right: **⚡ 1-2 ms**
mem --> dm: Liste de 8 appareils
dm --> cli: Retour
cli --> user: Affichage

== Scénario 2: Cache Mémoire Expiré → Disque ==
user -> cli: alexa device list
cli -> dm: get_devices()
dm -> mem: Vérifier TTL
mem -> mem: ❌ TTL > 5 min
dm -> cs: get("devices", ignore_ttl=True)
cs -> disk: Lire fichier
disk -> disk: ✅ Fichier existe\\n(toujours valide)
note right: **💾 10-50 ms**\\nPas de vérification TTL
disk --> cs: Données décompressées
cs --> dm: Liste de 8 appareils
dm -> mem: Mise à jour cache RAM
dm --> cli: Retour
cli --> user: Affichage

== Scénario 3: Pas de Cache → API ==
user -> cli: alexa device list
cli -> dm: get_devices()
dm -> mem: Vérifier TTL
mem -> mem: ❌ Vide (premier démarrage)
dm -> cs: get("devices", ignore_ttl=True)
cs -> disk: Lire fichier
disk -> disk: ❌ Fichier absent
cs --> dm: None
dm -> api: GET /api/devices-v2/device
note right: **🌐 200-1000 ms**\\nRéquête HTTP
api --> dm: Réponse JSON
dm -> disk: Sauvegarder (gzip)
dm -> mem: Sauvegarder (RAM)
dm --> cli: Retour
cli --> user: Affichage

@enduml
"""
    
    output_dir = Path(__file__).parent.parent / "docs" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "cache_flow_diagram.puml"
    output_file.write_text(content, encoding="utf-8")
    
    print(f"✅ Diagramme de flux généré: {output_file}")
    return output_file


def generate_architecture_puml():
    """Génère le diagramme d'architecture en PlantUML."""
    
    content = """@startuml cache_architecture
!theme plain
skinparam backgroundColor white
skinparam componentStyle rectangle

title Architecture du Système de Cache

package "Client Layer" {
    [CLI Commands] as cli
}

package "Business Logic" {
    [DeviceManager\\ncache_ttl=300s] as dm
}

package "Cache Layer" {
    package "Niveau 1 - Volatile" {
        database "In-Memory Cache\\nDict[str, List]\\nTTL: 5 min" as mem #Yellow
    }
    
    package "Niveau 2 - Persistent" {
        [CacheService\\nignore_ttl=True] as cs
        database "Disk Cache\\nJSON.GZ files\\nTTL: ∞ (pas de TTL)" as disk #LightCoral
    }
}

package "External API" {
    cloud "Amazon Alexa API" as api
}

cli --> dm : get_devices()
dm --> mem : Vérifier cache mémoire
dm --> cs : get(ignore_ttl=True)
cs --> disk : Lire fichier cache
dm --> api : Requête HTTP si aucun cache
api --> dm : Réponse JSON
dm --> mem : Mise à jour RAM
dm --> disk : Sauvegarde disque (via cs)

note right of mem
  **Cache chaud (hot cache)**
  - Latence: 1-2 ms
  - Durée: 5 minutes
  - Thread-safe: threading.Lock
end note

note right of disk
  **Cache de secours (fallback)**
  - Latence: 10-50 ms
  - Durée: ∞ (toujours valide)
  - Format: JSON compressé (gzip)
  - Taille: ~80% réduction
end note

note right of api
  **Dernier recours**
  - Latence: 200-1000 ms
  - Nécessite authentification
  - Rate limiting possible
end note

@enduml
"""
    
    output_dir = Path(__file__).parent.parent / "docs" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "cache_architecture.puml"
    output_file.write_text(content, encoding="utf-8")
    
    print(f"✅ Diagramme d'architecture généré: {output_file}")
    return output_file


def generate_state_machine_puml():
    """Génère le diagramme de machine à états du cache."""
    
    content = """@startuml cache_state_machine
!theme plain
skinparam backgroundColor white

title Machine à États du Cache

[*] --> Empty : Premier démarrage

state Empty {
    Empty : Cache mémoire: ∅
    Empty : Cache disque: ∅
}

state MemoryOnly {
    MemoryOnly : Cache mémoire: ✅ (< 5 min)
    MemoryOnly : Cache disque: ✅
}

state DiskOnly {
    DiskOnly : Cache mémoire: ❌ (expiré)
    DiskOnly : Cache disque: ✅ (toujours valide)
}

state BothValid {
    BothValid : Cache mémoire: ✅
    BothValid : Cache disque: ✅
}

Empty --> BothValid : API Call\\nSauvegarde mémoire + disque
BothValid --> DiskOnly : Attendre > 5 min\\nExpiration mémoire
DiskOnly --> BothValid : Lecture disque\\nRecharge mémoire
BothValid --> BothValid : get_devices()\\nCache mémoire valide\\n⚡ 1-2 ms
DiskOnly --> DiskOnly : get_devices()\\nLecture disque\\n💾 10-50 ms
Empty --> Empty : get_devices()\\nAppel API\\n🌐 200-1000 ms

note right of BothValid
  **État optimal**
  Performance maximale
  Pas d'I/O disque
  Pas de requête réseau
end note

note right of DiskOnly
  **État de secours**
  Après 5 min d'inactivité
  Lecture disque rapide
  Pas de requête réseau
end note

note right of Empty
  **État initial**
  Premier lancement
  Nécessite API call
  Initialise les caches
end note

@enduml
"""
    
    output_dir = Path(__file__).parent.parent / "docs" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "cache_state_machine.puml"
    output_file.write_text(content, encoding="utf-8")
    
    print(f"✅ Diagramme de machine à états généré: {output_file}")
    return output_file


def generate_performance_comparison_puml():
    """Génère un diagramme de comparaison de performances."""
    
    content = """@startuml cache_performance
!theme plain
skinparam backgroundColor white

title Comparaison des Performances - Cache vs API

|Utilisateur|
start
:Exécuter\\n**alexa device list**;

|Système|
if (Cache mémoire valide?) then (Oui)
  #LightGreen:Lire cache RAM;
  note right
    **⚡ ULTRA RAPIDE**
    Latence: 1-2 ms
    Probabilité: 80%
    (si < 5 min)
  end note
  |Utilisateur|
  #LightGreen:Afficher 8 appareils;
  stop
else (Non)
  if (Cache disque existe?) then (Oui)
    #Yellow:Lire fichier\\ndevices.json.gz;
    #Yellow:Décompresser;
    #Yellow:Charger en mémoire;
    note right
      **💾 RAPIDE**
      Latence: 10-50 ms
      Probabilité: 19%
      (après expiration)
      **PAS DE TTL**
    end note
    |Utilisateur|
    #Yellow:Afficher 8 appareils;
    stop
  else (Non)
    #Red:Appel API Amazon;
    #Red:GET /api/devices-v2/device;
    #Red:Parser JSON;
    #Red:Sauvegarder disque;
    #Red:Sauvegarder mémoire;
    note right
      **🌐 LENT**
      Latence: 200-1000 ms
      Probabilité: 1%
      (premier lancement)
    end note
    |Utilisateur|
    #Red:Afficher 8 appareils;
    stop
  endif
endif

@enduml
"""
    
    output_dir = Path(__file__).parent.parent / "docs" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "cache_performance.puml"
    output_file.write_text(content, encoding="utf-8")
    
    print(f"✅ Diagramme de performances généré: {output_file}")
    return output_file


def generate_markdown_includes():
    """Génère les inclusions Markdown pour CACHE_SYSTEM.md"""
    
    markdown = """
## 📊 Diagrammes

### Flux de Cache Multi-Niveaux

Le diagramme suivant illustre les trois scénarios possibles lors de la récupération de la liste des appareils :

```plantuml
@startuml
!include diagrams/cache_flow_diagram.puml
@enduml
```

![Cache Flow Diagram](diagrams/cache_flow_diagram.png)

### Architecture Globale

```plantuml
@startuml
!include diagrams/cache_architecture.puml
@enduml
```

![Cache Architecture](diagrams/cache_architecture.png)

### Machine à États

Le cache évolue entre différents états selon l'utilisation :

```plantuml
@startuml
!include diagrams/cache_state_machine.puml
@enduml
```

![Cache State Machine](diagrams/cache_state_machine.png)

### Comparaison de Performances

```plantuml
@startuml
!include diagrams/cache_performance.puml
@enduml
```

![Cache Performance](diagrams/cache_performance.png)

---

**Note:** Pour visualiser les diagrammes PlantUML :
- Dans VS Code: Installer l'extension `PlantUML` (jebbs.plantuml)
- En ligne: Copier le contenu .puml sur http://www.plantuml.com/plantuml/
- En local: `java -jar plantuml.jar docs/diagrams/*.puml`
"""
    
    output_dir = Path(__file__).parent.parent / "docs"
    output_file = output_dir / "CACHE_DIAGRAMS_INCLUDES.md"
    output_file.write_text(markdown, encoding="utf-8")
    
    print(f"\n📝 Inclusions Markdown générées: {output_file}")
    return output_file


if __name__ == "__main__":
    print("🎨 Génération des diagrammes PlantUML du système de cache...\n")
    
    try:
        files = [
            generate_cache_flow_puml(),
            generate_architecture_puml(),
            generate_state_machine_puml(),
            generate_performance_comparison_puml(),
        ]
        
        markdown_file = generate_markdown_includes()
        
        print("\n✅ Tous les diagrammes PlantUML ont été générés avec succès!")
        print(f"📁 Emplacement: docs/diagrams/")
        print(f"\n📄 Fichiers générés:")
        for f in files:
            print(f"   - {f.name}")
        
        print(f"\n💡 Pour visualiser les diagrammes:")
        print(f"   1. Installer l'extension VS Code 'PlantUML' (jebbs.plantuml)")
        print(f"   2. Ouvrir un fichier .puml")
        print(f"   3. Appuyer sur Alt+D pour prévisualiser")
        print(f"\n📋 Pour intégrer dans CACHE_SYSTEM.md:")
        print(f"   Copier le contenu de: {markdown_file.name}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        raise
