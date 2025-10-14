#!/usr/bin/env node
'use strict';

/**
 * @fileoverview Utilitaires communs pour la gestion des cookies Alexa
 * @module utils
 */

const fs = require('fs');
const path = require('path');

/**
 * Parse une chaîne de cookies en tableau d'objets
 * @param {string} cookieString - Chaîne de cookies séparés par ';'
 * @returns {Array<{name: string, value: string}>} Tableau de cookies
 */
function parseCookieString(cookieString) {
    if (!cookieString) return [];
    
    return cookieString
        .split(/;\s*/)
        .map((entry) => {
            const [name, ...valueParts] = entry.split('=');
            if (!name || valueParts.length === 0) return null;
            
            const value = valueParts.join('=').replace(/^"|"$/g, '');
            return { name: name.trim(), value: value.trim() };
        })
        .filter(Boolean);
}

/**
 * Construit un Map de cookies à partir d'un résultat Alexa
 * @param {Object} result - Résultat contenant loginCookie, localCookie, cookie
 * @returns {Map<string, string>} Map des cookies (nom -> valeur)
 */
function buildCookieJar(result) {
    const jar = new Map();
    
    const sources = [
        result.loginCookie,
        result.localCookie,
        result.cookie
    ].filter(Boolean);
    
    for (const source of sources) {
        for (const cookie of parseCookieString(source)) {
            jar.set(cookie.name, cookie.value);
        }
    }
    
    return jar;
}

/**
 * Écrit un fichier cookie au format Netscape
 * @param {Object} result - Résultat contenant les cookies et amazonPage
 * @param {string} outputPath - Chemin du fichier de sortie
 */
function writeCookieTxt(result, outputPath) {
    const domain = result.amazonPage 
        ? (result.amazonPage.startsWith('.') ? result.amazonPage : `.${result.amazonPage}`)
        : '.amazon.fr';
    
    const expiry = Math.floor(Date.now() / 1000) + 30 * 24 * 3600; // 30 jours
    
    const header = [
        '# Netscape HTTP Cookie File',
        '# https://curl.haxx.se/rfc/cookie_spec.html',
        '# This is a generated file! Do not edit.',
        ''
    ];
    
    const jar = buildCookieJar(result);
    const lines = [];
    
    for (const [name, value] of jar.entries()) {
        const secure = /token|sess|csrf|at/i.test(name) ? 'TRUE' : 'FALSE';
        lines.push(`${domain}\tTRUE\t/\t${secure}\t${expiry}\t${name}\t${value}`);
    }
    
    fs.writeFileSync(outputPath, header.concat(lines).join('\n'), 'utf8');
}

/**
 * Sauvegarde le résultat complet dans un fichier JSON
 * @param {Object} result - Résultat de la récupération du cookie
 * @param {Object} alexaCookie - Instance alexaCookie pour construire la config
 * @param {string} jsonPath - Chemin du fichier JSON de sortie
 * @param {string} cookieTxtPath - Chemin du fichier cookie.txt
 */
function saveResult(result, alexaCookie, jsonPath, cookieTxtPath) {
    const configAlexaRemote = alexaCookie.construireConfigAlexaRemote(result);
    
    const payload = {
        recapitulatif: {
            cookie: configAlexaRemote.cookie,
            csrf: configAlexaRemote.csrf,
            macDms: configAlexaRemote.macDms,
            refreshToken: result.refreshToken,
            tokenDate: result.tokenDate
        },
        donneesCompletes: result
    };
    
    // Créer les répertoires si nécessaire
    const jsonDir = path.dirname(jsonPath);
    const cookieDir = path.dirname(cookieTxtPath);
    
    if (!fs.existsSync(jsonDir)) {
        fs.mkdirSync(jsonDir, { recursive: true });
        console.log(`Répertoire créé: ${jsonDir}`);
    }
    
    if (!fs.existsSync(cookieDir)) {
        fs.mkdirSync(cookieDir, { recursive: true });
        console.log(`Répertoire créé: ${cookieDir}`);
    }
    
    // Sauvegarder le JSON
    fs.writeFileSync(jsonPath, JSON.stringify(payload, null, 2), 'utf8');
    console.log(`Résultat JSON enregistré dans ${jsonPath}`);
    
    // Sauvegarder le cookie.txt
    writeCookieTxt(result, cookieTxtPath);
    console.log(`Fichier cookie Netscape enregistré dans ${cookieTxtPath}`);
}

/**
 * Charge le fichier de résultat JSON
 * @param {string} jsonPath - Chemin du fichier JSON
 * @returns {Object} Données du fichier JSON
 * @throws {Error} Si le fichier n'existe pas ou est invalide
 */
function loadResultFile(jsonPath) {
    if (!fs.existsSync(jsonPath)) {
        throw new Error(`Fichier ${jsonPath} non trouvé`);
    }
    
    try {
        const content = fs.readFileSync(jsonPath, 'utf8');
        return JSON.parse(content);
    } catch (error) {
        throw new Error(`Erreur de lecture du fichier JSON: ${error.message}`);
    }
}

/**
 * Vérifie si le cookie en cache est encore valide
 * @param {string} jsonPath - Chemin du fichier de cache JSON
 * @param {number} maxAgeHours - Durée de validité en heures (défaut: 24h)
 * @returns {Object|null} Données du cache si valide, null sinon
 */
function checkCachedCookie(jsonPath, maxAgeHours = 24) {
    try {
        if (!fs.existsSync(jsonPath)) {
            console.log('Aucun cookie en cache trouvé');
            return null;
        }
        
        const data = loadResultFile(jsonPath);
        
        // Vérifier la présence des données essentielles
        if (!data.recapitulatif || !data.recapitulatif.cookie || !data.recapitulatif.csrf) {
            console.log('Cookie en cache incomplet');
            return null;
        }
        
        // Vérifier l'âge du cookie
        const tokenDate = data.recapitulatif.tokenDate || data.donneesCompletes?.tokenDate;
        if (tokenDate) {
            const ageMs = Date.now() - tokenDate;
            const ageHours = ageMs / (1000 * 60 * 60);
            
            if (ageHours > maxAgeHours) {
                console.log(`Cookie en cache expiré (âge: ${ageHours.toFixed(1)}h)`);
                return null;
            }
            
            console.log(`Cookie en cache valide (âge: ${ageHours.toFixed(1)}h)`);
        } else {
            console.log('Cookie en cache sans date, considéré comme valide');
        }
        
        return data;
    } catch (error) {
        console.log(`Erreur lors de la vérification du cache: ${error.message}`);
        return null;
    }
}

/**
 * Détecte l'adresse IP du réseau local
 * @returns {string} Adresse IP ou '127.0.0.1' par défaut
 */
function detectLocalIp() {
    const os = require('os');
    const envIp = process.env.ALEXA_COOKIE_PROXY_IP;
    
    if (envIp) return envIp;
    
    const ifaces = os.networkInterfaces();
    for (const name of Object.keys(ifaces)) {
        for (const iface of ifaces[name]) {
            if (iface.family === 'IPv4' && !iface.internal) {
                return iface.address;
            }
        }
    }
    
    return '127.0.0.1';
}

/**
 * Ouvre une URL dans le navigateur par défaut
 * @param {string} url - URL à ouvrir
 */
function openBrowser(url) {
    const { spawn } = require('child_process');
    
    console.log(`Ouverture du navigateur sur ${url}`);
    
    let command;
    let args;
    
    if (process.platform === 'darwin') {
        command = 'open';
        args = [url];
    } else if (process.platform === 'win32') {
        command = 'cmd';
        args = ['/c', 'start', '""', url];
    } else {
        command = 'xdg-open';
        args = [url];
    }
    
    const child = spawn(command, args, { stdio: 'ignore', detached: true });
    child.unref();
}

/**
 * Vérifie et installe les dépendances npm si nécessaire
 * @param {string} packageDir - Répertoire du package
 */
function ensureDependencies(packageDir) {
    const { spawnSync } = require('child_process');
    const packageJson = require(path.join(packageDir, 'package.json'));
    const deps = Object.assign(
        {},
        packageJson.dependencies || {},
        packageJson.devDependencies || {}
    );
    
    const missing = [];
    for (const dep of Object.keys(deps)) {
        try {
            require.resolve(dep, { paths: [packageDir] });
        } catch (err) {
            missing.push(dep);
        }
    }
    
    if (missing.length) {
        console.log('Installation des dépendances manquantes...', missing.join(', '));
        const result = spawnSync('npm', ['install'], {
            cwd: packageDir,
            stdio: 'inherit'
        });
        
        if (result.status !== 0) {
            throw new Error('Échec de l\'installation des dépendances.');
        }
    }
}

/**
 * Crée un logger formaté
 * @param {string} prefix - Préfixe pour les messages de log
 * @returns {Function} Fonction de logging
 */
function createLogger(prefix = 'Alexa-Cookie') {
    return (message) => {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] ${prefix}: ${message}`);
    };
}

/**
 * Gère les erreurs de manière centralisée
 * @param {Error} error - Erreur à gérer
 * @param {string} context - Contexte de l'erreur
 * @param {number} exitCode - Code de sortie (0 = pas de sortie)
 */
function handleError(error, context = 'Opération', exitCode = 1) {
    console.error(`ERREUR [${context}]: ${error.message}`);
    
    if (error.stack && process.env.DEBUG) {
        console.error('Stack trace:', error.stack);
    }
    
    if (exitCode > 0) {
        process.exit(exitCode);
    }
}

module.exports = {
    parseCookieString,
    buildCookieJar,
    writeCookieTxt,
    saveResult,
    loadResultFile,
    checkCachedCookie,
    detectLocalIp,
    openBrowser,
    ensureDependencies,
    createLogger,
    handleError
};
