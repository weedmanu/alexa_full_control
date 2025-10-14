/**
 * @fileoverview Constantes partagées pour l'authentification Amazon Alexa
 * Centralise toutes les valeurs de configuration utilisées par la bibliothèque
 */

'use strict';

// ============================================================================
// CONFIGURATION AMAZON
// ============================================================================

/**
 * Page Amazon par défaut (domaine)
 */
const DEFAULT_AMAZON_PAGE = 'amazon.fr';

/**
 * User-Agent par défaut pour Windows
 */
const DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36';

/**
 * User-Agent pour Linux
 */
const DEFAULT_USER_AGENT_LINUX = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36';

/**
 * User-Agent pour macOS (commenté pour l'instant)
 */
// const DEFAULT_USER_AGENT_MACOS = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36';

/**
 * Message HTML affiché après succès de l'authentification
 */
const DEFAULT_PROXY_CLOSE_WINDOW_HTML = '<b>Cookie Amazon Alexa récupéré avec succès. Vous pouvez fermer le navigateur.</b>';

/**
 * Langue acceptée par défaut
 */
const DEFAULT_ACCEPT_LANGUAGE = 'fr-FR';

// ============================================================================
// API ALEXA
// ============================================================================

/**
 * Version de l'API Alexa
 */
const API_CALL_VERSION = '2.2.651540.0';

/**
 * User-Agent pour les appels API
 */
const API_CALL_USER_AGENT = 'AmazonWebView/Amazon Alexa/2.2.651540.0/iOS/18.3.1/iPhone';

/**
 * Nom de l'application par défaut
 */
const DEFAULT_APP_NAME = 'Alexa Voice Control CLI';

// ============================================================================
// ENDPOINTS CSRF
// ============================================================================

/**
 * Liste des endpoints possibles pour récupérer le token CSRF
 * Utilisés pour valider l'authentification
 */
const CSRF_OPTIONS = [
    '/api/language',
    '/spa/index.html',
    '/api/devices-v2/device?cached=false',
    '/templates/oobe/d-device-pick.handlebars',
    '/api/strings'
];

// ============================================================================
// CONFIGURATION PROXY
// ============================================================================

/**
 * Port par défaut du serveur proxy
 */
const DEFAULT_PROXY_PORT = 3456;

/**
 * Port par défaut du serveur OAuth
 */
const DEFAULT_PROXY_OAUTH_PORT = 3457;

/**
 * Timeout par défaut pour les requêtes HTTP (ms)
 */
const DEFAULT_HTTP_TIMEOUT = 10000;

// ============================================================================
// CONFIGURATION RETRY
// ============================================================================

/**
 * Nombre maximum de tentatives pour les requêtes
 */
const MAX_RETRY_ATTEMPTS = 3;

/**
 * Délai entre les tentatives (ms)
 */
const RETRY_DELAY = 2000;

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
    // Amazon
    DEFAULT_AMAZON_PAGE,
    DEFAULT_USER_AGENT,
    DEFAULT_USER_AGENT_LINUX,
    DEFAULT_PROXY_CLOSE_WINDOW_HTML,
    DEFAULT_ACCEPT_LANGUAGE,
    
    // API
    API_CALL_VERSION,
    API_CALL_USER_AGENT,
    DEFAULT_APP_NAME,
    
    // CSRF
    CSRF_OPTIONS,
    
    // Proxy
    DEFAULT_PROXY_PORT,
    DEFAULT_PROXY_OAUTH_PORT,
    DEFAULT_HTTP_TIMEOUT,
    
    // Retry
    MAX_RETRY_ATTEMPTS,
    RETRY_DELAY
};
