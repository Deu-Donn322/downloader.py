# -*- coding: utf-8 -*-

import os
import logging
import re
import shutil
from flask import Flask
from threading import Thread
from yt_dlp import YoutubeDL, utils as ytdlp_utils
from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔐 --- VOTRE JETON TELEGRAM --- 🔐
# REMPLACEZ LA LIGNE CI-DESSOUS PAR VOTRE VRAI JETON DE BOT
TOKEN = "7922618318:AAFeTFXCnfVNLj6xuWQIoIBh73IPhAhutwc"

# 📝 --- CONFIGURATION DU JOURNAL (LOGGING) --- 📝
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# 🌐 --- MINI SERVEUR WEB POUR MAINTENIR LE BOT ACTIF --- 🌐
app = Flask(__name__)

@app.route('/')
def home():
    """ Affiche un message simple pour confirmer que le bot est en ligne. """
    return "✅ Bot TikTok est actif et fonctionnel !"

def run_flask():
    """ Lance le serveur Flask. """
    # Désactive les journaux par défaut de Flask pour une console plus propre
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """ Lance le serveur Flask dans un thread séparé pour ne pas bloquer le bot. """
    t = Thread(target=run_flask)
    t.start()


# ✨ --- NOUVELLE FONCTION : NETTOYAGE D'URL --- ✨
def clean_tiktok_url(url: str) -> str:
    """
    Extrait l'URL de base d'un lien TikTok en supprimant les paramètres de suivi.
    Exemple: https://vm.tiktok.com/ZM... -> https://www.tiktok.com/@user/video/123...
    """
    match = re.search(r'(https?://www\.tiktok\.com/(@[^/]+)/(video|photo)/(\d+))', url)
    if match:
        clean_url = match.group(1)
        logger.info(f"URL nettoyée: {clean_url}")
        return clean_url
    logger.warning("Impossible de nettoyer l'URL, utilisation de l'originale.")
    return url


# 📥 --- FONCTION DE TÉLÉCHARGEMENT --- 📥
def download_media(url, download_path):
    """
    Télécharge tous les médias (vidéo ou images) d'une URL TikTok.
    Retourne une liste des chemins des fichiers téléchargés.
    """
    os.makedirs(download_path, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(download_path, '%(title).50s_%(autonumber)s.%(ext)s'),
        'quiet': True,
        'noplaylist': False,
        'retries': 10,
        'socket_timeout': 1000,
        # Ajout d'un User-Agent pour simuler un navigateur et éviter les blocages
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
        }
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
        
        downloaded_files = [os.path.join(download_path, f) for f in os.listdir(download_path)]
        return downloaded_files
    except Exception as e:
        logger.error(f"Échec du téléchargement avec yt-dlp: {e}")
        return []


# 🎯 --- GESTION DES MESSAGES UTILISATEUR --- 🎯
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Traite les messages texte contenant un lien TikTok.
    """
    chat_id = update.effective_chat.id
    raw_url = update.message.text.strip()

    if "tiktok.com" not in raw_url:
        await update.message.reply_text("❌ Lien invalide. Veuillez m'envoyer un lien TikTok.")
        return

    # Nettoie l'URL avant de l'utiliser
    url = clean_tiktok_url(raw_url)
    
    download_dir = f"temp_{chat_id}_{update.message.message_id}"
    status_message = None
    try:
        status_message = await update.message.reply_text("⏳ Traitement du lien...")
        
        filenames = download_media(url, download_dir)

        if not filenames:
            await status_message.edit_text("❌ Échec du téléchargement. Le lien est peut-être invalide, privé ou le format n'est pas supporté.")
            return

        await status_message.edit_text("✅ Téléchargement terminé ! Envoi en cours...")

        # Cas 1: Plusieurs fichiers (diaporama de photos)
        if len(filenames) > 1:
            media_group = [InputMediaPhoto(media=open(filename, "rb")) for filename in sorted(filenames)]
            await context.bot.send_media_group(chat_id=chat_id, media=media_group, write_timeout=60)

        # Cas 2: Un seul fichier (vidéo ou autre)
        elif len(filenames) == 1:
            filename = filenames[0]
            with open(filename, "rb") as media_file:
                if os.path.getsize(filename) < 50 * 1024 * 1024 and filename.lower().endswith('.mp4'):
                    await context.bot.send_video(chat_id=chat_id, video=media_file, write_timeout=60)
                else:
                    await context.bot.send_document(chat_id=chat_id, document=media_file, write_timeout=60)
        
        await status_message.delete()

    except Exception as e:
        logger.error(f"Erreur inattendue dans handle_message: {e}")
        if status_message:
            await status_message.edit_text("❌ Une erreur est survenue. Veuillez réessayer.")
    finally:
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)


# 🟢 --- COMMANDE /START --- 🟢
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Envoie un message de bienvenue. """
    await update.message.reply_text("👋 Bonjour ! Envoyez-moi un lien TikTok pour télécharger la vidéo ou les photos.")


# 🚀 --- DÉMARRAGE DU BOT --- 🚀
def main():
    """ Construit et lance le bot Telegram. """
    keep_alive()

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Le bot TikTok est lancé et prêt à fonctionner.")
    application.run_polling()

if __name__ == "__main__":
    main()

       
