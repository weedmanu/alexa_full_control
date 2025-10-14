#!/usr/bin/env node

'use strict';

/**
 * @fileoverview Script CLI pour récupérer le cookie Alexa avec authentification
 * Support pour authentification automatique (email/password/MFA) ou manuelle via proxy
 */

const path = require('path');
const yargs = require('yargs/yargs');
const {
    detectLocalIp,
    openBrowser,
    ensureDependencies,
    saveResult,
    createLogger,
    handleError,
    checkCachedCookie
} = require('./utils/common.js');

// Configuration des chemins
const packageDir = __dirname;
const projectRoot = path.join(__dirname, '..');

// Vérification et installation des dépendances
try {
    ensureDependencies(packageDir);
} catch (error) {
    handleError(error, 'Installation des dépendances', 1);
}

// Chargement du module alexa-cookie après vérification des dépendances
const alexaCookie = require(path.join(packageDir, 'alexa-cookie-lib.js'));

// Logger personnalisé
const logger = createLogger('Alexa-Cookie-CLI');

// Parse des arguments de ligne de commande
const argv = yargs(process.argv.slice(2))
    .usage('Usage: $0 [options]')
    .option('email', {
        describe: 'Email du compte Amazon',
        type: 'string',
    })
    .option('password', {
        describe: 'Mot de passe du compte Amazon',
        type: 'string',
    })
    .option('mfaSecret', {
        describe: 'Clé secrète MFA/2FA (si pas de SMS)',
        type: 'string',
    })
    .option('proxyHost', {
        describe: 'Hôte du proxy (défaut: localhost)',
        type: 'string',
        default: 'localhost',
    })
    .option('proxyPort', {
        describe: 'Port du proxy (défaut: 3456)',
        type: 'number',
        default: 3456,
    })
    .option('no-sandbox', {
        describe: 'Désactiver le sandboxing (utile pour debug)',
        type: 'boolean',
        default: false,
    })
    .option('amazonPage', {
        describe: 'Page Amazon à utiliser (défaut: amazon.fr)',
        type: 'string',
        default: process.env.AMAZON_DOMAIN || 'amazon.fr',
    })
    .option('language', {
        describe: 'Langue (défaut: fr-FR)',
        type: 'string',
        default: process.env.LANGUAGE || 'fr-FR',
    })
    .help()
    .argv;

/**
 * Configuration des options pour alexa-cookie
 */
function buildAlexaCookieOptions() {
    const proxyOwnIp = detectLocalIp();
    
    const options = {
        logger: logger,
        proxyOnly: true,
        setupProxy: true,
        proxyOwnIp,
        proxyPort: parseInt(process.env.ALEXA_COOKIE_PROXY_PORT, 10) || argv.proxyPort,
        proxyListenBind: '0.0.0.0',
        proxyLogLevel: 'info',
        amazonPage: argv.amazonPage,
        acceptLanguage: argv.language,
        amazonPageProxyLanguage: argv.language.replace('-', '_')
    };
    
    // Ajouter le secret MFA si fourni
    if (argv.mfaSecret || process.env.MFA_SECRET) {
        options.otpSecret = argv.mfaSecret || process.env.MFA_SECRET;
        logger('Configuration MFA/2FA détectée');
    }
    
    return options;
}

/**
 * Gère l'ouverture du navigateur pour l'authentification manuelle
 */
function handleBrowserAuth(err) {
    if (!err) return false;
    
    const match = err.message && err.message.match(/http:\/\/[^\s']+/);
    if (!match) {
        handleError(err, 'Authentification', 1);
        return true;
    }
    
    const url = match[0];
    if (!browserOpened) {
        browserOpened = true;
        openBrowser(url);
        logger('Navigateur ouvert. Veuillez compléter la connexion Amazon (2FA si nécessaire)');
    }
    
    return true;
}

/**
 * Traite le résultat de la récupération du cookie
 */
function handleCookieResult(err, result) {
    // Si erreur sans résultat, tenter l'ouverture du navigateur
    if (err && !result) {
        handleBrowserAuth(err);
        return;
    }
    
    // Erreur avec résultat partiel
    if (err) {
        handleError(err, 'Récupération du cookie', 1);
        return;
    }
    
    // Succès
    logger('Cookie récupéré avec succès');
    
    try {
        const dataDir = path.join(projectRoot, 'data');
        const jsonPath = path.join(dataDir, 'cookie-resultat.json');
        const cookieTxtPath = path.join(dataDir, 'cookie.txt');
        
        saveResult(result, alexaCookie, jsonPath, cookieTxtPath);
        
        logger('Tous les fichiers ont été sauvegardés');
        
        // Arrêter le serveur proxy
        alexaCookie.stopProxyServer(() => {
            logger('Proxy arrêté. Vous pouvez fermer cette fenêtre.');
            process.exit(0);
        });
    } catch (saveError) {
        handleError(saveError, 'Sauvegarde des résultats', 1);
    }
}

/**
 * Point d'entrée principal
 */
function main() {
    logger('Initialisation de la récupération du cookie Alexa');
    
    // Définir les chemins des fichiers de cache
    const dataDir = path.join(projectRoot, 'data');
    const jsonPath = path.join(dataDir, 'cookie-resultat.json');
    const cookieTxtPath = path.join(dataDir, 'cookie.txt');
    
    // Vérifier d'abord le cache (24h de validité)
    const cachedCookie = checkCachedCookie(jsonPath, 24);
    if (cachedCookie) {
        logger('✓ Cookie valide trouvé en cache, aucune nouvelle authentification nécessaire');
        logger(`Cookie: ${cachedCookie.recapitulatif.cookie.substring(0, 50)}...`);
        logger(`CSRF: ${cachedCookie.recapitulatif.csrf}`);
        
        // Arrêter immédiatement sans lancer le proxy
        process.exit(0);
        return;
    }
    
    // Pas de cache valide, procéder à l'authentification
    logger('Aucun cookie valide en cache, lancement de l\'authentification...');
    
    // Récupération des credentials
    const email = argv.email || process.env.EMAIL || '';
    const password = argv.password || process.env.PASSWORD || '';
    
    // Configuration des options
    const options = buildAlexaCookieOptions();
    
    // Afficher le mode d'authentification
    if (email && password) {
        logger(`Mode authentification automatique avec l'email: ${email}`);
    } else {
        logger('Mode authentification manuelle via proxy/navigateur');
    }
    
    // Lancer la récupération du cookie
    alexaCookie.generateAlexaCookie(email, password, options, handleCookieResult);
}

// État pour éviter les ouvertures multiples du navigateur
let browserOpened = false;

// Gestion des erreurs globales
process.on('uncaughtException', (error) => {
    handleError(error, 'Exception non capturée', 1);
});

process.on('unhandledRejection', (reason, promise) => {
    handleError(new Error(`Promesse rejetée: ${reason}`), 'Rejet non géré', 1);
});

// Gestion de l'interruption utilisateur (Ctrl+C)
process.on('SIGINT', () => {
    logger('Interruption utilisateur détectée');
    
    alexaCookie.stopProxyServer(() => {
        logger('Proxy arrêté');
        process.exit(130);
    });
});

// Lancement du script
if (require.main === module) {
    main();
}

module.exports = { main };
