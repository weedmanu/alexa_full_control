from utils.short_help_formatter import ShortHelpFormatter
from utils.short_help_formatter import strip_ansi_codes

actions = [
    {"action": "auth", "description": "Commande d'authentification Alexa."},
    {"action": "device communicate", "description": "Commande pour communiquer avec les appareils Alexa et envoyer un message important qui pourrait Ãªtre long."},
    {"action": "list", "description": "Lister tous les appareils disponibles."},
]

out = ShortHelpFormatter.format_short_help(
    category="device",
    emoji="ðŸ“±",
    title="DEVICE - Gestion des appareils",
    usage_patterns=["alexa device <ACTION> [OPTIONS]"],
    actions=actions,
    examples=["alexa device list", "alexa device communicate --to Kitchen"],
    global_examples=["alexa --verbose device list"],
)

print(strip_ansi_codes(out))

