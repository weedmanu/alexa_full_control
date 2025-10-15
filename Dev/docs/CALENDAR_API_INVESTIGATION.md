# 📅 Investigation API Calendrier Alexa

**Date** : 12 octobre 2025  
**Projet** : Alexa Advanced Control  
**Statut** : Endpoints trouvés mais accès bloqué

---

## 🎯 Objectif

Déterminer s'il existe une API REST pour accéder aux événements du calendrier Alexa (synchronisés depuis Google Calendar, Microsoft Outlook, Apple Calendar).

---

## 🔍 Résultats de l'Investigation

### Endpoints Testés

| Endpoint                                 | Méthode | Status | Résultat                        |
| ---------------------------------------- | ------- | ------ | ------------------------------- |
| `/alexa-privacy/apd/calendar`            | GET     | 403    | ✅ **Endpoint existe** (bloqué) |
| `/alexa-privacy/apd/calendar`            | POST    | 403    | ✅ **Endpoint existe** (bloqué) |
| `/alexa-privacy/apd/calendar/events`     | GET     | 403    | ✅ **Endpoint existe** (bloqué) |
| `/alexa-privacy/apd/calendar/events`     | POST    | 403    | ✅ **Endpoint existe** (bloqué) |
| `/alexa-privacy/apd/rvh/calendar-events` | POST    | 403    | ✅ **Endpoint existe** (bloqué) |
| `/api/calendar/events`                   | GET     | 404    | ❌ N'existe pas                 |
| `/api/calendar-events`                   | GET     | 404    | ❌ N'existe pas                 |
| `/api/namedLists?listType=CALENDAR`      | GET     | 404    | ❌ N'existe pas                 |

### Headers Utilisés

```http
csrf: <token_csrf_standard>
anti-csrftoken-a2z: <token_csrf_privacy>
Content-Type: application/json; charset=UTF-8
```

---

## 🔒 Conclusion : Accès Bloqué par Confidentialité

### Pourquoi 403 Forbidden ?

Les endpoints **existent** (`/alexa-privacy/apd/calendar*`) mais retournent systématiquement **403 Forbidden**, ce qui signifie :

1. **Les endpoints sont fonctionnels** (sinon ce serait 404 Not Found)
2. **L'authentification de base est valide** (CSRF tokens acceptés)
3. **Un mécanisme de protection supplémentaire bloque l'accès**

### Mécanisme de Protection

Amazon protège les données du calendrier avec plusieurs couches :

#### Niveau 1 : CSRF Standard

- Token `csrf` requis pour toutes les API
- ✅ **Validé** (nous l'avons)

#### Niveau 2 : CSRF Privacy

- Token `anti-csrftoken-a2z` pour les API Privacy
- ✅ **Validé** (nous l'avons)

#### Niveau 3 : Consentement Calendrier ⚠️

- **Token de consentement spécifique** aux événements calendrier
- ❌ **Manquant** → 403 Forbidden
- Probablement obtenu via un flux OAuth ou consentement explicite dans l'app Alexa

---

## 📱 Solution Alternative : TextCommand

Puisque l'API REST calendrier est inaccessible pour des raisons de confidentialité, la solution implémentée utilise **TextCommand** (commandes vocales simulées) :

### Fonctionnement

```python
# Au lieu de GET /api/calendar/events
voice_service.speak("quels sont mes événements aujourd'hui", device_serial)
```

### Avantages

- ✅ **Fonctionne** sans token de consentement supplémentaire
- ✅ Alexa énonce vocalement les événements sur l'appareil
- ✅ Respecte le modèle de confidentialité d'Amazon

### Limitations

- ❌ **Pas de données structurées** (JSON) retournées
- ❌ Réponse uniquement vocale sur l'appareil
- ❌ Impossible de parser/extraire les événements programmatiquement

---

## 🎤 Commandes TextCommand Implémentées

| Période       | Commande vocale                           | Paramètre `--days` |
| ------------- | ----------------------------------------- | ------------------ |
| Aujourd'hui   | "quels sont mes événements aujourd'hui"   | 1                  |
| Demain        | "quels sont mes événements demain"        | 2                  |
| Cette semaine | "quels sont mes événements cette semaine" | 3-7                |
| Ce mois       | "quels sont mes événements ce mois"       | 8+                 |

### Exemple d'utilisation

```bash
# Consulter les événements aujourd'hui
python alexa calendar list --device "Salon Echo" --days 1

# Consulter les événements de la semaine
python alexa calendar list --device "Salon Echo" --days 7
```

---

## 🔮 Pistes pour Débloquer l'API REST (Non Implémentées)

### Option 1 : Token de Consentement

Analyser le trafic réseau de l'application mobile Alexa pour identifier :

- Comment obtenir le token de consentement calendrier
- Endpoint pour demander le consentement (`/api/privacy/consent` ?)
- Scope/permissions spécifiques requis

### Option 2 : Simulation App Mobile

Se faire passer complètement pour l'application mobile officielle :

- User-Agent mobile exact
- Device fingerprint mobile
- Tokens supplémentaires (device token, app token)

### Option 3 : Alexa API Publique

Utiliser l'**Alexa Skills Kit (ASK)** avec le scope `alexa::profile:email:read` :

- Nécessite création d'une skill Alexa officielle
- Consentement explicite de l'utilisateur
- API publique documentée mais limitée

---

## 📝 Recommandation

**Conserver l'approche TextCommand actuelle** car :

1. ✅ **Fonctionne immédiatement** sans configuration complexe
2. ✅ **Respecte le modèle de sécurité** d'Amazon
3. ✅ **Pas de risque de blocage** (commandes vocales = usage normal)
4. ⚠️ Les tentatives de contournement (token scraping, etc.) pourraient :
   - Violer les ToS Amazon
   - Entraîner le blocage du compte
   - Casser lors de changements de sécurité

---

## 🛠️ Fichiers Modifiés

- `core/calendar/calendar_manager.py` : Méthodes `query_events()` + `test_privacy_api_endpoints()`
- `cli/commands/calendar.py` : Action `test` pour exploration d'endpoints
- `cli/context.py` : Injection `config` + `device_manager` dans CalendarManager

---

## 📚 Références

- **APIs Amazon.md** : Documentation des API privées Alexa
- **API_ENDPOINTS_INVENTORY.md** : Inventaire complet des endpoints testés
- **Activity Manager** : Implémentation Privacy API pour l'historique vocal (fonctionne avec le même mécanisme CSRF)
