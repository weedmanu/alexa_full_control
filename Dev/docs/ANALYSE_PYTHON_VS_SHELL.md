# 🔍 Analyse Comparative: Python CLI vs Script Shell

**Date**: 8 octobre 2025  
**Objectif**: Rendre le CLI Python aussi performant et complet que le script shell

---

## 📊 Résumé Exécutif

| Aspect                 | Script Shell (.sh)    | CLI Python            | Gap                  |
| ---------------------- | --------------------- | --------------------- | -------------------- |
| **Authentification**   | ✅ Refresh Token      | ✅ Refresh Token      | ✅ Équivalent        |
| **Liste Appareils**    | ✅ Complet            | ✅ Complet            | ✅ Équivalent        |
| **Contrôles Musique**  | ✅ Fonctionnel        | ✅ Fonctionnel        | ✅ Équivalent        |
| **État Player**        | ✅ **DÉTAILLÉ**       | ❌ **403 Forbidden**  | ⚠️ **CRITIQUE**      |
| **Queue/File**         | ✅ **DÉTAILLÉE**      | ❌ **Non implémenté** | ⚠️ **CRITIQUE**      |
| **Informations Media** | ✅ **JSON complet**   | ❌ **Limité**         | ⚠️ **IMPORTANT**     |
| **Volume**             | ✅ Cache local        | ✅ API directe        | ✅ Équivalent        |
| **TTS/Speak**          | ✅ Séquences          | ✅ VoiceCommand       | ✅ Équivalent        |
| **Multiroom**          | ✅ Créer/Supprimer    | ⚠️ Manager manquant   | ❌ **À IMPLÉMENTER** |
| **Bluetooth**          | ✅ Connect/Disconnect | ❌ Non implémenté     | ❌ **À IMPLÉMENTER** |

---

## 🎯 PROBLÈME CRITIQUE #1: État du Player

### ❌ Situation Actuelle (Python)

```python
# core/music/playback_manager.py:218
def get_state(self, device_serial: str, device_type: str) -> Optional[Dict]:
    """Récupère l'état actuel de la lecture.

    Note: L'endpoint /api/np/player retourne 403 Forbidden.
    Cette fonctionnalité n'est pas disponible via l'API Amazon.
    """
    logger.warning("get_state() appelé mais /api/np/player retourne 403 Forbidden")
    return None
```

**Résultat CLI Python**:

```bash
$ ./alexa music status -d "Salon Echo"
⚠️  L'état de la lecture n'est pas disponible via l'API Amazon
💡 Les contrôles musicaux (play/pause/next/stop) fonctionnent correctement
```

### ✅ Situation Script Shell

```bash
# scripts/alexa_remote_control.sh:870
show_queue()
{
  ${CURL} ${OPTS} -s -b ${COOKIE} -A "${BROWSER}" \
   -H "csrf: $(awk "\$0 ~/.${AMAZON}.*csrf[ \\s\\t]+/ {print \$7}" ${COOKIE})" \
   -X GET \
   "https://${ALEXA}/api/np/player?deviceSerialNumber=${DEVICESERIALNUMBER}&deviceType=${DEVICETYPE}${PARENT}"
}
```

**Résultat Script Shell**:

```json
{
  "playerInfo": {
    "infoText": {
      "subText1": "Mazzy Star",
      "subText2": "So Tonight That I Might See",
      "title": "Fade Into You"
    },
    "progress": {
      "mediaLength": 296,
      "mediaProgress": 194
    },
    "state": "PLAYING",
    "volume": {
      "muted": false,
      "volume": 50
    },
    "quality": {
      "codec": "flac",
      "dataRateInBitsPerSecond": 1681132,
      "samplingRateInHertz": 44100
    }
  }
}
```

### 🔧 SOLUTION

**Le problème n'est PAS l'API, c'est l'implémentation Python !**

Le script shell **FONCTIONNE** avec le même endpoint `/api/np/player`. Voici ce qui manque:

#### 1. **Headers Manquants**

```python
# ❌ Actuel (Python)
headers={"csrf": self.auth.csrf}

# ✅ Nécessaire (comme le shell)
headers={
    "csrf": self.auth.csrf,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:1.0) bash-script/1.0",
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": f"https://{self.config.alexa_domain}/spa/index.html",
    "Origin": f"https://{self.config.alexa_domain}",
    "Accept": "application/json",
    "Accept-Language": "fr-FR,fr;q=0.9"
}
```

#### 2. **Paramètre PARENT manquant**

```python
# Le script shell ajoute les infos du parent multiroom si nécessaire
PARENT=""
PARENTID=$(jq '.devices[] | select(.accountName == $device) | .parentClusters[0]')
if [ "$PARENTID" != "null" ] ; then
    PARENT="&lemurId=${PARENTID}&lemurDeviceType=${PARENTDEVICE}"
fi

# URL complète:
# /api/np/player?deviceSerialNumber=XXX&deviceType=YYY&lemurId=ZZZ&lemurDeviceType=AAA
```

#### 3. **Endpoints Multiples**

Le script shell interroge **3 endpoints** pour avoir les infos complètes:

```bash
# 1. État du player
GET /api/np/player?deviceSerialNumber=X&deviceType=Y

# 2. État média
GET /api/media/state?deviceSerialNumber=X&deviceType=Y

# 3. Queue complète
GET /api/np/queue?deviceSerialNumber=X&deviceType=Y
```

---

## 🎯 PROBLÈME CRITIQUE #2: File d'Attente (Queue)

### ❌ Actuel Python

```python
# core/music/playback_manager.py:49
def get_queue(self, device_serial: str, device_type: str) -> Optional[Dict]:
    """Récupère la file d'attente de lecture."""
    response = self.auth.session.get(
        f"https://{self.config.alexa_domain}/api/np/queue",
        params={"deviceSerialNumber": device_serial, "deviceType": device_type},
        headers={"csrf": self.auth.csrf},
    )
    return response.json()
```

**Résultat**: Fonction existe mais **jamais exposée dans le CLI** !

### ✅ Script Shell

Retourne la **queue complète** avec 5 morceaux suivants, artwork, artistes, etc.

### 🔧 SOLUTION

1. **Ajouter l'action `queue` au CLI**:

```python
# cli/commands/music.py
queue_parser = subparsers.add_parser("queue", help="Afficher la file d'attente")
queue_parser.add_argument("-d", "--device", required=True)
```

2. **Améliorer les headers** (même problème que get_state)

---

## 🎯 PROBLÈME #3: Multiroom Manager Manquant

### ❌ Actuel Python

```python
# cli/commands/multiroom.py:149
if not self.context.multiroom_mgr:
    self.error("MultiroomManager non disponible")
    return False
```

**Erreur**:

```
AttributeError: 'Context' object has no attribute 'multiroom_mgr'
```

### ✅ Script Shell

```bash
# Supprimer multiroom
delete_multiroom() {
  curl -X DELETE "https://${ALEXA}/api/lemur/tail/${DEVICESERIALNUMBER}"
}

# Créer multiroom
create_multiroom() {
  JSON='{"id":null,"name":"'${LEMUR}'","members":['${DEVICES}']}'
  curl -X POST -d "${JSON}" "https://${ALEXA}/api/lemur/tail"
}
```

### 🔧 SOLUTION

Créer `/home/manu/Documents/GitHub/alexa_advanced_control-dev-cli/core/multiroom_manager.py`:

```python
class MultiroomManager:
    """Gestionnaire des groupes multiroom (multi-pièces)."""

    def get_groups(self) -> List[Dict]:
        """Liste tous les groupes multiroom."""
        # Filtrer devices avec deviceFamily == "WHA"

    def create_group(self, name: str, device_serials: List[str], primary_serial: str) -> bool:
        """Crée un groupe multiroom."""
        # POST /api/lemur/tail

    def delete_group(self, group_serial: str) -> bool:
        """Supprime un groupe multiroom."""
        # DELETE /api/lemur/tail/{serial}
```

Et l'ajouter au contexte:

```python
# cli/context.py
@property
def multiroom_mgr(self):
    if self._multiroom_mgr is None and self.auth:
        from core.multiroom_manager import MultiroomManager
        self._multiroom_mgr = MultiroomManager(self.auth, self.state_machine)
    return self._multiroom_mgr
```

---

## 🎯 PROBLÈME #4: Bluetooth Non Implémenté

### ❌ Actuel Python

Aucune commande Bluetooth !

### ✅ Script Shell

```bash
# Lister appareils BT
list_bluetooth() {
  curl "https://${ALEXA}/api/bluetooth?cached=false"
}

# Connecter BT
connect_bluetooth() {
  curl -X POST -d '{"bluetoothDeviceAddress":"'${BLUETOOTH}'"}' \
    "https://${ALEXA}/api/bluetooth/pair-sink/${DEVICETYPE}/${DEVICESERIALNUMBER}"
}

# Déconnecter BT
disconnect_bluetooth() {
  curl -X POST \
    "https://${ALEXA}/api/bluetooth/disconnect-sink/${DEVICETYPE}/${DEVICESERIALNUMBER}"
}
```

### 🔧 SOLUTION

Créer `core/audio/bluetooth_manager.py` (déjà existe mais incomplet).

---

## 📋 Plan d'Action Priorisé

### 🔴 PRIORITÉ CRITIQUE (Bloquer 100% audit)

1. **Corriger get_state() pour qu'il fonctionne** ⏱️ 30 min

   - Ajouter tous les headers du script shell
   - Gérer le paramètre PARENT (lemurId)
   - Tester sur "Salon Echo"

2. **Exposer la queue dans le CLI** ⏱️ 20 min
   - Ajouter action `queue` à `music.py`
   - Afficher les 5 prochains morceaux
   - Format JSON + Format texte

### 🟠 PRIORITÉ HAUTE (Compléter les fonctionnalités)

3. **Implémenter MultiroomManager** ⏱️ 1h

   - Créer le manager
   - L'ajouter au Context
   - Tester create/delete/list

4. **Compléter BluetoothManager** ⏱️ 45 min
   - Implémenter list/connect/disconnect
   - Ajouter commandes CLI

### 🟡 PRIORITÉ MOYENNE (Améliorer l'UX)

5. **Améliorer affichage status musique** ⏱️ 30 min

   - Afficher artwork (URL)
   - Afficher progression (3:14 / 4:56)
   - Afficher qualité audio (FLAC, bitrate)
   - Afficher provider (Amazon Music, Spotify)

6. **Ajouter cache volume local** ⏱️ 20 min
   - Comme le script shell (`/tmp/.alexa.volume.*`)
   - Éviter requêtes API répétées

---

## 🛠️ Modifications Immédiates Recommandées

### Fichier 1: `core/music/playback_manager.py`

```python
def get_state(self, device_serial: str, device_type: str, parent_id: str = None, parent_type: str = None) -> Optional[Dict]:
    """Récupère l'état complet de la lecture (comme le script shell)."""
    with self._lock:
        if not self.state_machine.can_execute_commands:
            return None

        try:
            # Construire params comme le script shell
            params = {
                "deviceSerialNumber": device_serial,
                "deviceType": device_type
            }

            # Ajouter parent si multiroom
            if parent_id:
                params["lemurId"] = parent_id
                params["lemurDeviceType"] = parent_type

            # Headers complets comme le script shell
            headers = {
                "csrf": self.auth.csrf,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:1.0) bash-script/1.0",
                "DNT": "1",
                "Connection": "keep-alive",
                "Referer": f"https://{self.config.alexa_domain}/spa/index.html",
                "Origin": f"https://{self.config.alexa_domain}",
                "Content-Type": "application/json; charset=UTF-8"
            }

            # 1. État du player
            player_response = self.breaker.call(
                self.auth.session.get,
                f"https://{self.config.alexa_domain}/api/np/player",
                params=params,
                headers=headers,
                timeout=10
            )
            player_response.raise_for_status()

            # 2. État média
            media_response = self.breaker.call(
                self.auth.session.get,
                f"https://{self.config.alexa_domain}/api/media/state",
                params={"deviceSerialNumber": device_serial, "deviceType": device_type},
                headers=headers,
                timeout=10
            )
            media_response.raise_for_status()

            # 3. Queue
            queue_response = self.breaker.call(
                self.auth.session.get,
                f"https://{self.config.alexa_domain}/api/np/queue",
                params={"deviceSerialNumber": device_serial, "deviceType": device_type},
                headers=headers,
                timeout=10
            )
            queue_response.raise_for_status()

            # Combiner les 3 réponses
            return {
                "player": player_response.json(),
                "media": media_response.json(),
                "queue": queue_response.json()
            }

        except Exception as e:
            logger.error(f"Erreur récupération état: {e}")
            return None
```

### Fichier 2: `cli/commands/music.py`

Ajouter après le parser "status":

```python
# Action: queue
queue_parser = subparsers.add_parser(
    "queue",
    help="Afficher la file d'attente",
    description="Affiche la liste des morceaux en attente de lecture."
)
queue_parser.add_argument(
    "-d", "--device",
    type=str,
    required=True,
    metavar="DEVICE_NAME",
    help="Nom de l'appareil cible"
)
```

Et implémenter:

```python
def _show_queue(self, args: argparse.Namespace) -> bool:
    """Afficher la file d'attente (comme le script shell)."""
    try:
        serial = self.get_device_serial(args.device)
        if not serial:
            return False

        device_type = self._get_device_type(args.device)

        # Récupérer état complet
        state = self.call_with_breaker(
            self.context.playback_mgr.get_state,
            serial,
            device_type
        )

        if not state:
            self.warning("Impossible de récupérer la queue")
            return False

        # Afficher comme le script shell
        if hasattr(args, "json_output") and args.json_output:
            print(json.dumps(state, indent=2, ensure_ascii=False))
        else:
            self._display_complete_queue(state)

        return True

    except Exception as e:
        self.logger.exception("Erreur affichage queue")
        self.error(f"Erreur: {e}")
        return False

def _display_complete_queue(self, state: Dict) -> None:
    """Affiche la queue comme le script shell."""
    player = state.get("player", {}).get("playerInfo", {})
    queue = state.get("queue", {}).get("queueInfo", {}).get("media", [])

    # Morceau en cours
    if player:
        info = player.get("infoText", {})
        progress = player.get("progress", {})
        quality = player.get("quality", {})

        print("\n🎵 En cours de lecture:\n")
        print(f"  Titre: {info.get('title', 'N/A')}")
        print(f"  Artiste: {info.get('subText1', 'N/A')}")
        print(f"  Album: {info.get('subText2', 'N/A')}")

        if progress:
            current = progress.get("mediaProgress", 0)
            total = progress.get("mediaLength", 0)
            print(f"  Progression: {current//60}:{current%60:02d} / {total//60}:{total%60:02d}")

        if quality:
            codec = quality.get("stats", {}).get("codec", "N/A")
            bitrate = quality.get("stats", {}).get("dataRateInBitsPerSecond", 0)
            samplerate = quality.get("stats", {}).get("samplingRateInHertz", 0)
            print(f"  Qualité: {codec.upper()} {samplerate//1000}kHz {bitrate//1000}kbps")

    # Prochains morceaux
    if queue:
        print(f"\n📋 File d'attente ({len(queue)} morceaux):\n")
        for i, track in enumerate(queue[:5], 1):
            info = track.get("infoText", {})
            print(f"  {i}. {info.get('title', 'N/A')} - {info.get('subText1', 'N/A')}")
```

---

## 🎯 Résultat Attendu

Après ces modifications, le CLI Python devrait donner **EXACTEMENT** le même résultat que le script shell:

```bash
$ ./alexa music status -d "Salon Echo"

🎵 En cours de lecture:

  Titre: Fade Into You
  Artiste: Mazzy Star
  Album: So Tonight That I Might See
  Progression: 3:14 / 4:56
  Qualité: FLAC 44kHz 1681kbps

📋 File d'attente (5 morceaux):

  1. Fade Into You - Mazzy Star
  2. misses - Dominic Fike
  3. Trouble - Cage The Elephant
  4. How Soon Is Now? - The Smiths
  5. Lovers Rock - TV Girl
```

---

## 📊 Conclusion

**Le script shell fonctionne PARFAITEMENT car il:**

1. ✅ Utilise les **bons headers HTTP**
2. ✅ Gère les **appareils multiroom** (PARENT)
3. ✅ Interroge **plusieurs endpoints** pour avoir toutes les infos
4. ✅ Implémente **toutes les fonctionnalités** (BT, multiroom, queue)

**Le CLI Python doit simplement:**

1. 🔧 **Copier les headers du script shell**
2. 🔧 **Gérer les parents multiroom**
3. 🔧 **Combiner les 3 endpoints** (player, media, queue)
4. 🔧 **Implémenter les managers manquants** (multiroom, bluetooth)

**Temps estimé total**: **~4 heures** pour avoir un CLI Python au niveau du script shell.

---

_Document généré le 8 octobre 2025 - Analyse comparative complète_
