import os
import logging
from yt_dlp import YoutubeDL, utils as ytdlp_utils
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ✅ Ton token (remplace si besoin)
TOKEN = "7922618318:AAFeTFXCnfVNLj6xuWQIoIBh73IPhAhutwc"

# 🔧 Log setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 📥 Fonction de téléchargement TikTok vidéo
def download_video(url, chat_id):
    ydl_opts = {
        "outtmpl": f"{chat_id}_%(title).50s.%(ext)s",
        "format": "mp4",
        "merge_output_format": "mp4",
        "quiet": True,
        "noplaylist": True,
        "retries": 10,
        "socket_timeout": 1000,
        "concurrent_fragment_downloads": 5,
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }]
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# 🎯 Réponse à un message texte
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    url = update.message.text.strip()

    # Vérifie que c'est un lien TikTok
    if "tiktok.com" not in url:
        await update.message.reply_text("❌ Je ne supporte actuellement que les vidéos TikTok.")
        return

    # Téléchargement vidéo
    try:
        await update.message.reply_text("⏳ Téléchargement de la vidéo TikTok en cours...")
        filename = download_video(url, chat_id)

        if not os.path.exists(filename):
            await update.message.reply_text("❌ Le fichier n'a pas été trouvé.")
            return

        size = os.path.getsize(filename)
        with open(filename, "rb") as video_file:
            if size < 50 * 1024 * 1024:
                await context.bot.send_video(chat_id=chat_id, video=video_file)
            else:
                await context.bot.send_document(chat_id=chat_id, document=video_file)

        os.remove(filename)

    except ytdlp_utils.DownloadError as e:
        logger.error(f"Erreur yt-dlp : {e}")
        await update.message.reply_text("❌ Impossible de télécharger la vidéo.")
    except Exception as e:
        logger.error(f"Erreur inattendue : {e}")
        await update.message.reply_text("❌ Une erreur est survenue pendant le téléchargement.")

# 🟢 Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Envoie-moi un lien TikTok pour télécharger une vidéo.")

# ▶️ Lancement du bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🚀 Bot TikTok lancé avec succès.")
    app.run_polling()

if __name__ == "__main__":
    main()
