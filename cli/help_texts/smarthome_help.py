"""Help text constants for the `smarthome` command.

Contains the long description and short per-action descriptions used by the
smarthome command parser.
"""

SMARTHOME_DESCRIPTION = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏠  CONTRÔLE DOMOTIQUE ALEXA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

\033[1;32m🎯 Fonctionnalités principales:\033[0m
  • Contrôle complet des appareils intelligents
  • Gestion des serrures connectées et sécurité
  • Contrôle des éclairages et interrupteurs
  • Surveillance des capteurs et caméras
  • Automatisation domotique intégrée

\033[1;34m🏗️  Architecture modulaire:\033[0m
  • Interface unifiée pour tous appareils connectés
  • Support multi-protocoles (Zigbee, Z-Wave, etc.)
  • Cache intelligent des états d'appareils
  • Gestion des scènes et automatisation

Usage: alexa [OPTIONS_GLOBALES] smarthome [<ACTION>] [OPTIONS_ACTION]

\033[1;91m🎯 Actions disponibles:\033[0m
  list        Lister tous les appareils intelligents connectés
  info        Afficher les informations détaillées d'un appareil
  control     Allumer/éteindre un appareil (on/off/toggle)
  lock        Verrouiller une serrure connectée
  unlock      Déverrouiller une serrure connectée
  status      Afficher l'état actuel d'un appareil

\033[1;35m⚙️  Options d\'action:\033[0m
  list:
    --filter KEYWORD        Filtrer par nom ou type
    --type TYPE             Filtrer par type (switch/plug/lock/sensor/camera/fan/blind/garage/valve/other)
  info:
    --entity ENTITY_ID      ID de l'entité (ex: switch.salon)
  control:
    --entity ENTITY_ID      ID de l'entité (requis)
    --operation OPERATION   Opération (requis: on/off/toggle)
  lock/unlock:
    --entity ENTITY_ID      ID de l'entité serrure (ex: lock.entree)
    --code CODE             Code de sécurité (optionnel/requis selon l'action)
  status:
    --entity ENTITY_ID      ID de l'entité (requis)

\033[1;36m📋 Processus détaillé:\033[0m
  1. Sélection de l'action domotique souhaitée
  2. Validation des paramètres et options fournies
  3. Exécution de l'opération sur les appareils connectés
  4. Mise à jour du cache et retour du résultat

\033[1;37m💡 Exemples d\'utilisation:\033[0m
  alexa smarthome list
  alexa smarthome list --type switch
  alexa smarthome list --filter salon
  alexa smarthome info --entity switch.salon
  alexa smarthome control --entity switch.salon --operation on
  alexa smarthome lock --entity lock.entree
  alexa smarthome unlock --entity lock.entree --code 1234
  alexa smarthome status --entity sensor.temperature

\033[1;90m💡 Pour plus d\'aide:\033[0m
  alexa smarthome list --help
  alexa smarthome control --help
  alexa smarthome lock --help

\033[1;31m⚠️ Prérequis essentiels:\033[0m
  • Authentification valide avec Alexa
  • Connexion internet active
  • Appareils connectés au compte Amazon
"""

LIST_HELP = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 LISTE DES APPAREILS INTELLIGENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

\033[1;32m🎯 Fonctionnalités principales:\033[0m
  • Lister tous les appareils connectés
  • Filtrage par type ou nom

\033[1;34m🏗️  Architecture modulaire:\033[0m
  • Récupération depuis l'API domotique
  • Mise en cache des appareils

\033[1;36mUsage:\033[0m \033[1;37malexa\033[0m \033[1;32msmarthome\033[0m \033[1;33mlist\033[0m [\033[1;35mOPTIONS\033[0m]

\033[1;35m⚙️  Options d\'action:\033[0m
  --filter KEYWORD        Filtrer par nom ou type
  --type TYPE             Filtrer par type (switch/plug/lock/sensor/camera/fan/blind/garage/valve/other)

\033[1;36m📋 Processus détaillé:\033[0m
  1. Connexion aux services domotiques Alexa
  2. Récupération de la liste complète des appareils
  3. Application des filtres si spécifiés
  4. Formatage et affichage avec types et statuts

\033[1;36m💡 Exemples d\'utilisation:\033[0m
  alexa smarthome list
  alexa smarthome list --type switch
  alexa smarthome list --filter salon

\033[1;37m💡 Pour plus d\'aide:\033[0m
  alexa smarthome info --help

\033[1;31m⚠️ Prérequis essentiels:\033[0m
  • Authentification valide pour accès aux appareils
  • Au moins un appareil connecté
"""

INFO_HELP = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ℹ️  INFORMATIONS DÉTAILLÉES D'UN APPAREIL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

\033[1;32m🎯 Fonctionnalités principales:\033[0m
  • Afficher toutes les informations d'un appareil
  • Voir capacités et configuration

\033[1;34m🏗️  Architecture modulaire:\033[0m
  • Récupération détaillée depuis l'API
  • Analyse des capacités

\033[1;36mUsage:\033[0m \033[1;37malexa\033[0m \033[1;32msmarthome\033[0m \033[1;33minfo\033[0m [\033[1;35mOPTIONS\033[0m]

\033[1;35m⚙️  Options d\'action:\033[0m
  --entity ENTITY_ID      ID de l'entité (ex: switch.salon)

\033[1;36m📋 Processus détaillé:\033[0m
  1. Recherche de l'appareil par son identifiant
  2. Récupération des informations complètes depuis Alexa
  3. Analyse des capacités et fonctionnalités disponibles
  4. Formatage structuré des informations détaillées

\033[1;36m💡 Exemples d\'utilisation:\033[0m
  alexa smarthome info --entity switch.salon

\033[1;37m💡 Pour plus d\'aide:\033[0m
  alexa smarthome list --help

\033[1;31m⚠️ Prérequis essentiels:\033[0m
  • Appareil doit exister dans la configuration
  • ID d'entité valide
"""

CONTROL_HELP = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎛️  CONTRÔLE D'UN APPAREIL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

\033[1;32m🎯 Fonctionnalités principales:\033[0m
  • Contrôler l'état d'un appareil
  • Allumer, éteindre ou basculer

\033[1;34m🏗️  Architecture modulaire:\033[0m
  • Envoi de commandes via l'API
  • Validation des opérations

\033[1;36mUsage:\033[0m \033[1;37malexa\033[0m \033[1;32msmarthome\033[0m \033[1;33mcontrol\033[0m [\033[1;35mOPTIONS\033[0m]

\033[1;35m⚙️  Options d\'action:\033[0m
  --entity ENTITY_ID      ID de l'entité (requis)
  --operation OPERATION   Opération (requis: on/off/toggle)

\033[1;36m📋 Processus détaillé:\033[0m
  1. Validation de l'appareil et de l'opération demandée
  2. Vérification de la compatibilité de l'appareil avec l'opération
  3. Envoi de la commande aux services Alexa
  4. Confirmation de l'exécution et mise à jour du cache

\033[1;36m💡 Exemples d\'utilisation:\033[0m
  alexa smarthome control --entity switch.salon --operation on
  alexa smarthome control --entity switch.salon --operation toggle

\033[1;37m💡 Pour plus d\'aide:\033[0m
  alexa smarthome status --help

\033[1;31m⚠️ Prérequis essentiels:\033[0m
  • Appareil doit supporter l'opération demandée
  • ID d'entité valide
"""

LOCK_HELP = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒 VERROUILLAGE D'UNE SERRURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

\033[1;32m🎯 Fonctionnalités principales:\033[0m
  • Verrouiller une serrure connectée
  • Sécuriser l'accès

\033[1;34m🏗️  Architecture modulaire:\033[0m
  • Commande sécurisée via l'API
  • Validation des permissions

\033[1;36mUsage:\033[0m \033[1;37malexa\033[0m \033[1;32msmarthome\033[0m \033[1;33mlock\033[0m [\033[1;35mOPTIONS\033[0m]

\033[1;35m⚙️  Options d\'action:\033[0m
  --entity ENTITY_ID      ID de l'entité serrure (ex: lock.entree)
  --code CODE             Code de sécurité (optionnel)

\033[1;36m📋 Processus détaillé:\033[0m
  1. Validation de l'identité de la serrure et des permissions
  2. Vérification de l'état actuel de la serrure
  3. Envoi de la commande de verrouillage sécurisée
  4. Journalisation de l'action pour traçabilité

\033[1;36m💡 Exemples d\'utilisation:\033[0m
  alexa smarthome lock --entity lock.entree

\033[1;37m💡 Pour plus d\'aide:\033[0m
  alexa smarthome status --help

\033[1;31m⚠️ Prérequis essentiels:\033[0m
  • Permissions de sécurité sur la serrure
  • Serrure doit être de type compatible
"""

UNLOCK_HELP = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔓 DÉVERROUILLAGE D'UNE SERRURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

\033[1;32m🎯 Fonctionnalités principales:\033[0m
  • Déverrouiller une serrure connectée
  • Autoriser l'accès

\033[1;34m🏗️  Architecture modulaire:\033[0m
  • Commande sécurisée avec code
  • Journalisation des accès

\033[1;36mUsage:\033[0m \033[1;37malexa\033[0m \033[1;32msmarthome\033[0m \033[1;33munlock\033[0m [\033[1;35mOPTIONS\033[0m]

\033[1;35m⚙️  Options d\'action:\033[0m
  --entity ENTITY_ID      ID de l'entité serrure (ex: lock.entree)
  --code CODE             Code de sécurité (requis)

\033[1;36m📋 Processus détaillé:\033[0m
  1. Validation du code de sécurité fourni
  2. Vérification des permissions d'accès à la serrure
  3. Envoi de la commande de déverrouillage sécurisée
  4. Journalisation complète de l'action pour sécurité

\033[1;36m💡 Exemples d\'utilisation:\033[0m
  alexa smarthome unlock --entity lock.entree --code 1234

\033[1;37m💡 Pour plus d\'aide:\033[0m
  alexa smarthome status --help

\033[1;31m⚠️ Prérequis essentiels:\033[0m
  • Code de sécurité valide obligatoire
  • Permissions d'accès à la serrure
"""

STATUS_HELP = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 ÉTAT D'UN APPAREIL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

\033[1;32m🎯 Fonctionnalités principales:\033[0m
  • Afficher l'état actuel d'un appareil
  • Voir valeurs des capteurs

\033[1;34m🏗️  Architecture modulaire:\033[0m
  • Récupération temps réel
  • Formatage des données

\033[1;36mUsage:\033[0m \033[1;37malexa\033[0m \033[1;32msmarthome\033[0m \033[1;33mstatus\033[0m [\033[1;35mOPTIONS\033[0m]

\033[1;35m⚙️  Options d\'action:\033[0m
  --entity ENTITY_ID      ID de l'entité (requis)

\033[1;36m📋 Processus détaillé:\033[0m
  1. Recherche de l'appareil par son identifiant
  2. Récupération de l'état actuel en temps réel
  3. Formatage des données selon le type d'appareil
  4. Affichage avec indicateurs visuels d'état

\033[1;36m💡 Exemples d\'utilisation:\033[0m
  alexa smarthome status --entity sensor.temperature

\033[1;37m💡 Pour plus d\'aide:\033[0m
  alexa smarthome control --help

\033[1;31m⚠️ Prérequis essentiels:\033[0m
  • Appareil doit exister et être accessible
  • ID d'entité valide
"""

SMARTHOME_LIST_DESC = "Liste tous les appareils intelligents connectés."
SMARTHOME_INFO_DESC = "Affiche les informations détaillées d'un appareil."
SMARTHOME_CONTROL_DESC = "Contrôle l'état d'un appareil (on/off/toggle)."
SMARTHOME_LOCK_DESC = "Verrouille une serrure connectée."
SMARTHOME_UNLOCK_DESC = "Déverrouille une serrure connectée."
SMARTHOME_STATUS_DESC = "Affiche l'état actuel d'un appareil."

