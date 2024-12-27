import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import cohere
from PIL import Image, ImageDraw, ImageFont

# Configurez votre clé API Cohere
# COHERE_API_KEY = "UHkMZVRhulmF2mN4OVZczi5Sv0JCdMQqzFnNpl6m"
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
cohere_client = cohere.Client(COHERE_API_KEY)

# Configurez votre token de bot Telegram
# TELEGRAM_BOT_TOKEN = "6765617635:AAHSwllRRqHzRFo0NeJbAFl3IJR883B8brQ"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


if not TELEGRAM_BOT_TOKEN or not COHERE_API_KEY:
    raise ValueError("Les clés API sont manquantes. Assurez-vous qu'elles sont définies.")

# Code d'accès requis
ACCESS_CODE = "junior24"

# Informations sur le créateur
CREATOR_NAME = "Foko Junior"
CREATOR_BIO = (
    "Foko Junior est un développeur senior full-stack et un passionné de technologie, spécialisé dans la conception "
    "et le développement d'applications web et logicielles. Actuellement en 3ème année en Génie Logiciel, il maîtrise "
    "plusieurs technologies clés, notamment Python, PHP, JavaScript, ReactJS, Node.js, CSS, SQL, et bien d'autres.\n\n"
    "Avec un esprit créatif et une approche axée sur les résultats, Foko a travaillé sur des projets divers et innovants :\n"
    "- Gestion de stock pour Uniprice** : Développement d'une solution optimisée pour une gestion efficace des stocks.\n"
    "- Syndatech** : Création d'un site web moderne et interactif pour une entreprise technologique.\n"
    "- SyndaVoIP** : Développement d'une application web pour la gestion des PBX Asterisk.\n"
    "- Applications mathématiques** : Conception d'outils de gestion et d'analyse de graphes mathématiques.\n"
    "- Synda-WebRTC** : Projets en cours utilisant les technologies WebRTC pour la communication en temps réel.\n\n"
    "Au-delà du développement, Foko est également passionné par l'intelligence artificielle et s'efforce d'intégrer "
    "des solutions basées sur l'IA dans ses projets. Grâce à son dévouement et à sa polyvalence, il contribue activement "
    "à des projets complexes et à forte valeur ajoutée.\n\n"
    "Pour le contacter ou collaborer :\n"
    "- Email : benitojunior2022@gmail.com\n"
    "- WhatsApp : wa.me/690713130\n"
    "- Telegram : t.me/FokoJunior\n"
)

# Dictionnaire pour suivre l'état des utilisateurs
user_states = {}

# Configurez le logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Fonction pour gérer la commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    # Vérifiez si l'utilisateur est déjà authentifié
    if user_id in user_states and user_states[user_id] == 'authenticated':
        await update.message.reply_text(
            "Bienvenue à nouveau ! Vous pouvez maintenant poser vos questions."
        )
    else:
        user_states[user_id] = 'awaiting_code'
        await update.message.reply_text(
            "Bonjour ! Je suis Foko_Junior_bot, votre assistant personnel! Veuillez fournir le code d'accès pour commencer."
        )

# Fonction pour vérifier le code d'accès
async def check_access_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_message = update.message.text.strip()

    if user_states.get(user_id) == 'awaiting_code':  # L'utilisateur attend un code
        if user_message == ACCESS_CODE:
            user_states[user_id] = 'authenticated'  # Marque l'utilisateur comme authentifié
            await update.message.reply_text(
                "Code correct ! Vous êtes maintenant autorisé à discuter. Posez vos questions."
            )
        else:
            await update.message.reply_text("Code incorrect. Veuillez réessayer.")
    elif user_states.get(user_id) == 'authenticated':  # L'utilisateur est authentifié
        await handle_message(update, context)

# Fonction pour gérer les messages après la validation du code
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_message = update.message.text

    # Vérifier si l'utilisateur a déjà été authentifié
    if user_states.get(user_id) != 'authenticated':
        await update.message.reply_text("Vous devez d'abord fournir le code d'accès.")
        return

    try:
        # Vérifier si la question concerne le créateur
        if any(keyword in user_message.lower() for keyword in ["créateur", "développeur", "qui t'a créé", "qui est ton créateur", "qui ta concus", "à propos de ton créateur"]):
            await update.message.reply_text(
                f"Mon créateur est {CREATOR_NAME}. Voici quelques informations à son sujet :\n{CREATOR_BIO}"
            )
            return

        # Génération de réponse avec Cohere
        response = cohere_client.generate(
            model='command-xlarge-nightly',
            prompt=f"Utilisateur : {user_message}\nAssistant :",
            max_tokens=150,
            temperature=0.7,
        )
        cohere_reply = response.generations[0].text.strip()
        await update.message.reply_text(cohere_reply)
    except Exception as e:
        logging.error(f"Erreur lors de l'appel à l'API Cohere : {e}")
        await update.message.reply_text("Erreur : Impossible de répondre pour le moment.")

# Fonction principale pour exécuter le bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Gestionnaires de commandes et de messages
    app.add_handler(CommandHandler("start", start))  # Commande /start
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_access_code))  # Vérification du code d'accès
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Traitement des messages après validation du code

    app.run_polling()

if __name__ == "__main__":
    main()
