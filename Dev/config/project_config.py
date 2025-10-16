"""
Configuration du projet Alexa Advanced Control.

Classe de configuration principale.
"""


class Config:
    """Configuration principale."""

    def __init__(self, amazon_domain: str = "amazon.fr"):
        """
        Initialise la configuration.

        Args:
            amazon_domain: Domaine Amazon (amazon.fr, amazon.de, etc.)
        """
        self.amazon_domain = amazon_domain
        self.alexa_domain = f"alexa.{amazon_domain}"
