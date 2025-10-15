"""
Mapping des types et familles d'appareils Amazon Alexa.

Basé sur le repository alexa_media_player officiel :
https://github.com/alandtse/alexa_media_player/blob/master/custom_components/alexa_media/const.py

Auteur: M@nu
Date: 8 octobre 2025
"""

from typing import Any, Dict

# Mapping des codes de type Amazon vers les noms de produits réels
DEVICE_TYPE_MAPPING: Dict[str, str] = {
    # Echo Show Series
    "A2UONLFQW0PADH": "Echo Show 8 (Gen3)",
    "A15996VY63BQ2D": "Echo Show 8 (Gen2)",
    "A1Z88NGR2BK6A2": "Echo Show 8 (Gen1)",
    "A4ZP7ZC4PI6TO": "Echo Show 5 (Gen1)",
    "A1XWJRHALS1REP": "Echo Show 5 (Gen2)",
    "A11QM4H9HGV71H": "Echo Show 5 (Gen3)",
    "AIPK7MM90V7TB": "Echo Show 10 (Gen3)",
    "A1EIANJ7PNB0Q7": "Echo Show 15 (Gen1)",
    "A1NL4BVLQ4L3N3": "Echo Show (Gen1)",
    "AWZZ5CVHX2CD": "Echo Show (Gen2)",
    # Echo Dot Series
    "A1RABVCI4QCIKC": "Echo Dot (Gen3)",
    "A32DDESGESSHZA": "Echo Dot (Gen3)",
    "A32DOYMUN6DTXA": "Echo Dot (Gen3)",
    "A2U21SRK4QGSE1": "Echo Dot (Gen4)",
    "A3RMGO6LYLH7YN": "Echo Dot (Gen4)",
    "A2H4LV5GIZ1JFT": "Echo Dot Clock (Gen4)",
    "A4ZXE0RM7LQ7A": "Echo Dot (Gen5)",
    "A2DS1Q2TPDJ48U": "Echo Dot Clock (Gen5)",
    "A3S5BH2HU6VAYF": "Echo Dot (Gen2)",
    "AKNO1N0KSFN8L": "Echo Dot (Gen1)",
    # Echo Standard Series
    "AB72C64C86AW2": "Echo (Gen1)",
    "A7WXQPH584YP": "Echo (Gen2)",
    "A30YDR2MK8HMRV": "Echo (Gen3)",
    "A3FX4UWTP28V1P": "Echo (Gen3)",
    # Echo Plus Series
    "A2M35JJZWCQOMZ": "Echo Plus (Gen1)",
    "A18O6U1UQFJ0XK": "Echo Plus (Gen2)",
    # Echo Studio & Special
    "A3RBAYBE7VM004": "Echo Studio",
    "A3SSG6GR8UU7SN": "Echo Sub",
    "A27VEYGQBW3YR5": "Echo Link",
    "A2RU4B77X9R9NZ": "Echo Link Amp",
    "A3VRME03NAXFUB": "Echo Flex",
    "ASQZWP4GPYUT7": "Echo Pop",
    "A38949IHXHRQ5P": "Echo Tap",
    # Echo Auto
    "A13W6HQIHKEN3Z": "Echo Auto",
    "A195TXHV1M5D4A": "Echo Auto",
    "A303PJF6ISQ7IC": "Echo Auto",
    "ALT9P69K6LORD": "Echo Auto",
    # Echo Spot
    "A10A33FOX2NUBK": "Echo Spot (Gen1)",
    "A3EH2E0YZ30OD6": "Echo Spot (Gen2)",
    # Echo Frames & Buds
    "A3IYPH06PH1HRA": "Echo Frames",
    "A15QWUTQ6FSMYX": "Echo Buds (Gen2)",
    # Fire TV Series
    "A12GXV8XMS007S": "Fire TV (Gen1)",
    "A2E0SNTXJVT7WK": "Fire TV (Gen2)",
    "A1P7E7V3FCZKU6": "Fire TV (Gen3)",
    "A2GFL5ZMWNE0PX": "Fire TV (Gen3)",
    "A3HF4YRA2L7XGC": "Fire TV Cube",
    "A2JKHJ0PX4J3L3": "Fire TV Cube (Gen2)",
    "A1VGB7MHSIEYFK": "Fire TV Cube Gen3",
    "A265XOI9586NML": "Fire TV Stick",
    "ADVBD696BHNV5": "Fire TV Stick (Gen1)",
    "A2LWARUGJLBYEW": "Fire TV Stick (Gen2)",
    "A31DTMEEVDDOIV": "Fire TV Stick Lite",
    "AKPGW064GI9HE": "Fire TV Stick 4K (Gen3)",
    "A1WZKXFLI43K86": "Fire TV Stick MAX",
    # Mobile & Apps
    "A2IVLV5VM2W81": "PC Voice Python",
    "A2TF17PFR55MTB": "Alexa Mobile Voice Android",
    "A1RTAM01W29CUP": "Windows App",
    "A2WN1FJ2HG09UN": "Ultimate Alexa App",
    "A1ETW4IXK2PYBP": "Talk to Alexa",
    # Speaker Groups & Multi-room
    "A3C9PE6TNYLTCH": "Speaker Group",
    "AP1F6KUH00XPV": "Stereo/Subwoofer Pair",
    # TV & Third-party
    "A1LWUC82PS6F7I": "Smart TV (Alexa Built-in)",
    "A1X92YQU8MWAPD": "Third-party Media Display",
    "A1NQ0LXWBGVQS9": "Samsung QLED TV 2021",
    "A25OJWHZA1MWNB": "Samsung QLED TV 2021",
    "A1QKZ9D0IJY332": "Samsung TV 2020-U",
    "A324YMIUSWQDGE": "Samsung 8K TV",
    "A3GFRGUNIGG1I5": "Samsung TV QN50Q60CAGXZD",
    # Tablets
    "A1J16TEDOYCZTN": "Fire Tablet",
    "A2M4YX06LWP8WI": "Fire Tablet",
    "A1C66CX2XD756O": "Fire Tablet HD",
    "A38EHHIB10L47V": "Fire Tablet HD 8",
    "A3L0T0VL9A921N": "Fire Tablet HD 8",
    "AVU7CPPF2ZRAS": "Fire Tablet HD 8",
    "A2V9UEGZ82H4KZ": "Fire Tablet HD 10",
    "A3R9S4ZZECZ6YL": "Fire Tablet HD 10",
    "A2N49KXGVA18AR": "Fire Tablet HD 10 Plus",
    # Generic/Unknown
    "A12IZU8NMHSY5U": "Generic Device",
    "A39BU42XNMN516": "Generic Device",
    "A16MZVIFVHX6P6": "Generic Echo",
    "A25EC4GIHFOCSG": "Unrecognized Media Player",
    "A1ENT81UXFMNNO": "Unknown Device",
    "A1MUORL8FP149X": "Unknown Device",
    "A6SIQKETF3L2E": "Unknown Device",
}

# Mapping des familles d'appareils Amazon
DEVICE_FAMILY_MAPPING: Dict[str, str] = {
    "KNIGHT": "Echo Standard",
    "ROOK": "Echo Show",
    "WHA": "Whole Home Audio (Multi-room)",
    "VOX": "Voice Assistant App",
    "THIRD_PARTY_AVS_MEDIA_DISPLAY": "Third-party Display",
    "FIRE_TV": "Fire TV",
    "TABLET": "Fire Tablet",
    "UNKNOWN": "Unknown Type",
}

# Mapping des capacités vers descriptions lisibles
CAPABILITY_DESCRIPTIONS: Dict[str, str] = {
    "AUDIO_PLAYER": "Lecteur audio",
    "VOLUME_SETTING": "Contrôle volume",
    "MICROPHONE": "Microphone",
    "TIMERS_AND_ALARMS": "Timers et alarmes",
    "WAKE_WORD_SENSITIVITY": "Sensibilité mot d'activation",
    "FLASH_BRIEFING": "Flash briefing",
    "ALEXA_VOICE": "Assistant Alexa",
    "AMAZON_MUSIC": "Amazon Music",
    "SPOTIFY": "Spotify",
    "TUNE_IN": "TuneIn",
    "PANDORA": "Pandora",
    "I_HEART_RADIO": "iHeartRadio",
    "AUDIBLE": "Audible",
    "KINDLE_BOOKS": "Livres Kindle",
    "SUPPORTS_SOFTWARE_VERSION": "Mise à jour logicielle",
    "EQUALIZER_CONTROLLER_BASS": "Égaliseur (basses)",
    "EQUALIZER_CONTROLLER_MIDRANGE": "Égaliseur (médiums)",
    "EQUALIZER_CONTROLLER_TREBLE": "Égaliseur (aigus)",
    "BT_PAIRING_FLOW_V2": "Appairage Bluetooth",
    "PAIR_BT_SINK": "Récepteur Bluetooth",
    "CUSTOM_ALARM_TONE": "Sonneries d'alarme personnalisées",
    "SLEEP": "Mode veille",
    "REMINDERS": "Rappels",
    "FACE_TO_TALK": "Détection visuelle",
    "VISUAL_ID_ENHANCED_FACE_TO_TALK": "Reconnaissance faciale avancée",
    "GUARD_EARCON": "Alexa Guard",
    "ADAPTIVE_VOLUME": "Volume adaptatif",
    "ADAPTIVE_LISTENING": "Écoute adaptative",
}


def get_device_type_display_name(device_type: str) -> str:
    """
    Retourne le nom d'affichage lisible pour un type d'appareil.

    Args:
        device_type: Code de type Amazon (ex: "A2UONLFQW0PADH")

    Returns:
        Nom lisible de l'appareil (ex: "Echo Show 8 (Gen3)")
    """
    return DEVICE_TYPE_MAPPING.get(device_type, f"Unknown ({device_type})")


def get_device_display_name(device_family: str, device_type: str) -> str:
    """
    Retourne le nom d'affichage le plus spécifique possible.

    Priorité: device_type spécifique > device_family générique

    Args:
        device_family: Famille d'appareil
        device_type: Type d'appareil

    Returns:
        Nom d'affichage optimal
    """
    # Essayer d'abord le type spécifique
    specific_name = get_device_type_display_name(device_type)
    if specific_name != f"Unknown ({device_type})":  # Si on a trouvé un mapping
        return specific_name

    # Sinon utiliser la famille
    return get_family_display_name(device_family)


def get_family_display_name(device_family: str) -> str:
    """
    Retourne le nom d'affichage lisible pour une famille d'appareil.

    Args:
        device_family: Code de famille Amazon (ex: "KNIGHT")

    Returns:
        Nom lisible de la famille (ex: "Echo Standard")
    """
    return DEVICE_FAMILY_MAPPING.get(device_family, f"Unknown ({device_family})")


def get_capability_description(capability: str) -> str:
    """
    Retourne la description lisible d'une capacité.

    Args:
        capability: Code de capacité Amazon

    Returns:
        Description lisible de la capacité
    """
    return CAPABILITY_DESCRIPTIONS.get(capability, capability)


def format_device_info(device: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formate les informations d'un appareil avec des noms lisibles.

    Args:
        device: Dictionnaire avec les informations brutes de l'appareil

    Returns:
        Dictionnaire avec les informations formatées
    """
    formatted = device.copy()

    # Ajouter les noms lisibles
    if "deviceType" in device:
        formatted["deviceTypeDisplay"] = get_device_type_display_name(device["deviceType"])

    if "deviceFamily" in device:
        formatted["deviceFamilyDisplay"] = get_family_display_name(device["deviceFamily"])

    # Formater les capacités si présentes
    if "capabilities" in device:
        formatted["capabilitiesDisplay"] = [get_capability_description(cap) for cap in device["capabilities"]]

    return formatted
