# Bot Telegram de Téléchargement TikTok

Ce bot Telegram permet de télécharger des vidéos depuis TikTok.

## Fonctionnalités

- Télécharge des vidéos TikTok à partir d'un lien.
- Envoie les vidéos directement dans la conversation Telegram.

## Comment utiliser le bot

1.  Envoyez un lien TikTok au bot.
2.  Le bot téléchargera et vous enverra la vidéo correspondante.

## Configuration et Déploiement

### Prérequis

- Python 3.x
- Un token de bot Telegram (obtenu via BotFather)

### Installation locale (pour le développement)

1.  Clonez ce dépôt :
    ```bash
    git clone [https://github.com/votre_utilisateur/votre_depot.git](https://github.com/votre_utilisateur/votre_depot.git)
    cd votre_depot
    ```
2.  Créez et activez un environnement virtuel (recommandé) :
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Linux/macOS
    # ou
    .\venv\Scripts\activate   # Sur Windows
    ```
3.  Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```
4.  Définissez votre token de bot Telegram :
    Remplacez `"7922618318:AAFeTFXCnfVNLj6xuWQIoIBh73IPhAhutwc"` dans `downloader.py` par votre propre token, ou utilisez une variable d'environnement (recommandé pour la production).
    Exemple avec une variable d'environnement (`BOT_TOKEN`) :
    ```python
    TOKEN = os.environ.get("BOT_TOKEN") # Ajoutez `import os` en haut du fichier
    # Assurez-vous de définir cette variable d'environnement avant de lancer le bot
    ```
5.  Lancez le bot :
    ```bash
    python downloader.py
    ```

### Déploiement sur Railway

Ce projet est conçu pour être facilement déployé sur Railway. Assurez-vous d'avoir les fichiers `requirements.txt` et `Procfile` à la racine de votre dépôt.

**Variables d'environnement Railway :**
Si vous choisissez d'utiliser une variable d'environnement pour votre TOKEN, ajoutez une variable dans Railway sous l'onglet "Variables" :
- **Nom :** `BOT_TOKEN`
- **Valeur :** Votre token de bot Telegram (ex: `7922618318:AAFeTFXCnfVNLj6xuWQIoIBh73IPhAhutwc`)

Le `Procfile` indique à Railway de lancer le bot en exécutant `python downloader.py`.

---

## Auteur

Votre Nom / Votre Pseudo

---
