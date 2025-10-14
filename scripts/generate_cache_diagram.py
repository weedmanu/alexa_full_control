"""
Script de génération de diagramme du système de cache.

Génère un diagramme de flux montrant le processus de cache multi-niveaux
pour la récupération de la liste des appareils Alexa.

Prérequis:
    pip install diagrams graphviz

Usage:
    python scripts/generate_cache_diagram.py

Sortie:
    docs/diagrams/cache_flow_diagram.png
"""

from pathlib import Path
from diagrams import Diagram, Cluster, Edge
from diagrams.programming.framework import FastAPI
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.network import Internet
from diagrams.custom import Custom


def generate_cache_flow_diagram():
    """Génère le diagramme de flux du système de cache."""
    
    # Créer le dossier de sortie
    output_dir = Path(__file__).parent.parent / "docs" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configuration du diagramme
    graph_attr = {
        "fontsize": "14",
        "bgcolor": "white",
        "pad": "0.5",
    }
    
    node_attr = {
        "fontsize": "12",
    }
    
    with Diagram(
        "Système de Cache Multi-Niveaux - Device List",
        filename=str(output_dir / "cache_flow_diagram"),
        show=False,
        direction="TB",
        graph_attr=graph_attr,
        node_attr=node_attr,
    ):
        
        # Point d'entrée
        with Cluster("Commande CLI"):
            user_cmd = FastAPI("alexa device list")
        
        # Niveau 1: Cache Mémoire
        with Cluster("Niveau 1: Cache Mémoire (RAM)\nTTL: 5 minutes"):
            memory_cache = Redis("_devices_cache\n(Python variable)")
            memory_check = FastAPI("TTL valide?")
        
        # Niveau 2: Cache Disque
        with Cluster("Niveau 2: Cache Disque (Fallback)\nTTL: ∞ AUCUN"):
            disk_cache = PostgreSQL("devices.json.gz\n(compressed)")
            disk_check = FastAPI("Fichier existe?")
        
        # Niveau 3: API Amazon
        with Cluster("Niveau 3: API Amazon"):
            amazon_api = Internet("alexa.amazon.com\n/api/devices-v2/device")
        
        # Résultat
        with Cluster("Résultat"):
            output = FastAPI("Liste de 8 appareils")
        
        # Flux principal
        user_cmd >> Edge(label="1. Appel") >> memory_check
        
        # Scénario 1: Cache mémoire valide
        memory_check >> Edge(label="Oui (< 5min)\n⚡ 1-2ms", color="green", style="bold") >> memory_cache
        memory_cache >> Edge(label="RETOUR", color="green") >> output
        
        # Scénario 2: Cache mémoire expiré → Cache disque
        memory_check >> Edge(label="Non (> 5min)", color="orange") >> disk_check
        disk_check >> Edge(label="Oui (toujours valide)\n💾 10-50ms", color="blue", style="bold") >> disk_cache
        disk_cache >> Edge(label="Charge en mémoire", color="blue") >> memory_cache
        
        # Scénario 3: Cache disque absent → API
        disk_check >> Edge(label="Non (absent)", color="red") >> amazon_api
        amazon_api >> Edge(label="🌐 200-1000ms\nRéponse JSON", color="red", style="bold") >> disk_cache
        amazon_api >> Edge(label="Sauvegarde", color="red", style="dashed") >> memory_cache
    
    print(f"✅ Diagramme généré: {output_dir / 'cache_flow_diagram.png'}")


def generate_sequence_diagram():
    """Génère un diagramme de séquence détaillé."""
    
    output_dir = Path(__file__).parent.parent / "docs" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with Diagram(
        "Séquence de Cache - Démarrage Application",
        filename=str(output_dir / "cache_sequence_diagram"),
        show=False,
        direction="LR",
        graph_attr={"rankdir": "TB", "splines": "ortho"},
    ):
        
        # Acteurs
        with Cluster("Utilisateur"):
            user = FastAPI("CLI")
        
        with Cluster("DeviceManager"):
            device_mgr = FastAPI("get_devices()")
        
        with Cluster("CacheService"):
            cache_svc = PostgreSQL("get(ignore_ttl=True)")
        
        with Cluster("Amazon API"):
            api = Internet("HTTP GET")
        
        # Séquence
        user >> Edge(label="1. alexa device list") >> device_mgr
        device_mgr >> Edge(label="2. Cache mémoire vide\n(premier démarrage)") >> cache_svc
        cache_svc >> Edge(label="3. Fichier trouvé\n(ancien refresh)") >> device_mgr
        device_mgr >> Edge(label="4. Retour liste") >> user
    
    print(f"✅ Diagramme de séquence généré: {output_dir / 'cache_sequence_diagram.png'}")


def generate_architecture_diagram():
    """Génère un diagramme d'architecture globale."""
    
    output_dir = Path(__file__).parent.parent / "docs" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with Diagram(
        "Architecture du Système de Cache",
        filename=str(output_dir / "cache_architecture"),
        show=False,
        direction="LR",
    ):
        
        with Cluster("Client Layer"):
            cli = FastAPI("CLI Commands")
        
        with Cluster("Business Logic"):
            device_manager = FastAPI("DeviceManager\n(cache_ttl=300s)")
        
        with Cluster("Cache Layer"):
            with Cluster("Niveau 1 - Volatile"):
                mem_cache = Redis("In-Memory Cache\nDict[str, List]")
            
            with Cluster("Niveau 2 - Persistent"):
                disk_cache = PostgreSQL("Disk Cache\nJSON.GZ files")
                cache_service = FastAPI("CacheService\n(ignore_ttl)")
        
        with Cluster("External API"):
            amazon = Internet("Amazon Alexa API")
        
        # Relations
        cli >> device_manager
        device_manager >> mem_cache
        device_manager >> cache_service
        cache_service >> disk_cache
        device_manager >> amazon
    
    print(f"✅ Diagramme d'architecture généré: {output_dir / 'cache_architecture.png'}")


if __name__ == "__main__":
    print("🎨 Génération des diagrammes du système de cache...\n")
    
    try:
        generate_cache_flow_diagram()
        generate_sequence_diagram()
        generate_architecture_diagram()
        print("\n✅ Tous les diagrammes ont été générés avec succès!")
        print("📁 Emplacement: docs/diagrams/")
        print("\n💡 Pour les inclure dans le Markdown:")
        print("   ![Cache Flow](diagrams/cache_flow_diagram.png)")
        
    except ImportError as e:
        print(f"❌ Erreur: Bibliothèques manquantes")
        print(f"   {e}")
        print("\n💡 Installation requise:")
        print("   pip install diagrams graphviz")
        print("   Ou: pip install -r requirements-dev.txt")
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        raise
