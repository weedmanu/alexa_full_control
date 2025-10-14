#!/usr/bin/env node

'use strict';

/**
 * @fileoverview Script de rafraîchissement automatique du cookie Alexa
 * Utilise le refresh token stocké pour régénérer les cookies sans interaction utilisateur
 */

const path = require('path');
const alexaCookie = require('./alexa-cookie-lib.js');
const {
    loadResultFile,
    saveResult,
    createLogger,
    handleError
} = require('./utils/common.js');

// Configuration des chemins
const projectRoot = path.join(__dirname, '..');
const dataDir = path.join(projectRoot, 'data');
const jsonFile = path.join(dataDir, 'cookie-resultat.json');
const cookieTxtFile = path.join(dataDir, 'cookie.txt');

// Logger personnalisé
const logger = createLogger('Refresh-Cookie');

/**
 * Point d'entrée principal du script de rafraîchissement
 */
function refreshCookie() {
    logger('Démarrage du rafraîchissement automatique du cookie');
    
    let formerData;
    
    // Charger les données existantes
    try {
        const data = loadResultFile(jsonFile);
        formerData = data.donneesCompletes;
        
        if (!formerData) {
            throw new Error('Données complètes manquantes dans le fichier JSON');
        }
        
        logger('Données précédentes chargées avec succès');
    } catch (error) {
        handleError(error, 'Chargement des données', 1);
        return;
    }
    
    // Configuration pour le rafraîchissement
    const options = {
        formerRegistrationData: formerData,
        amazonPage: formerData.amazonPage || 'amazon.fr',
        baseAmazonPage: formerData.amazonPage || 'amazon.fr',
        logger: logger,
        proxyOnly: false
    };
    
    logger('Rafraîchissement du cookie avec le refresh token...');
    
    // Appel à la fonction de rafraîchissement
    alexaCookie.refreshAlexaCookie(options, (err, result) => {
        if (err) {
            handleError(err, 'Rafraîchissement du cookie', 1);
            return;
        }
        
        logger('Cookie rafraîchi avec succès');
        
        try {
            // Sauvegarder le résultat avec les utilitaires
            saveResult(result, alexaCookie, jsonFile, cookieTxtFile);
            logger('Tous les fichiers ont été mis à jour');
            
            process.exit(0);
        } catch (saveError) {
            handleError(saveError, 'Sauvegarde des résultats', 1);
        }
    });
}

// Gestion des erreurs non capturées
process.on('uncaughtException', (error) => {
    handleError(error, 'Exception non capturée', 1);
});

process.on('unhandledRejection', (reason, promise) => {
    handleError(new Error(`Promesse rejetée: ${reason}`), 'Rejet non géré', 1);
});

// Lancement du script
if (require.main === module) {
    refreshCookie();
}

module.exports = { refreshCookie };