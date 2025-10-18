"""
Utilitaires pour les commandes CLI.

Ce module contient des fonctions utilitaires utilisées par les commandes CLI.

Auteur: M@nu
Date: 18 octobre 2025
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
}

# Mapping des familles d'appareils
DEVICE_FAMILY_MAPPING: Dict[str, str] = {
    "KNIGHT": "Echo Standard",
    "ROOK": "Echo Plus",
    "ECHO": "Echo Standard",
    "SOUND_SYSTEM": "Echo Studio",
    "TABLET": "Echo Show",
    "WHA": "Echo Dot",
    "WHA_Clock": "Echo Dot Clock",
    "FIRE_TABLET": "Fire Tablet",
    "THIRD_PARTY_AVS": "Appareil tiers AVS",
    "UNKNOWN": "Inconnu",
}


def get_device_type_display_name(device_type: str) -> str:
    """
    Retourne le nom d'affichage pour un type d'appareil spécifique.

    Args:
        device_type: Code de type Amazon

    Returns:
        Nom d'affichage du type d'appareil
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