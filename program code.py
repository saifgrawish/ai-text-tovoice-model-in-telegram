!pip
install
edge - tts
python - telegram - bot
nest - asyncio

# Install required packages
!pip
install
edge - tts
python - telegram - bot == 20.7
pydub
!apt - get
install - y
ffmpeg

import os
import logging
import asyncio
import edge_tts
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import tempfile
import nest_asyncio

# Fix for Colab's event loop
nest_asyncio.apply()

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Available voices with languages
VOICES = {
    # English
    'en-US-AriaNeural': '🇺🇸 Aria (Female, US)',
    'en-US-GuyNeural': '🇺🇸 Guy (Male, US)',
    'en-US-JennyNeural': '🇺🇸 Jenny (Female, US)',
    'en-GB-SoniaNeural': '🇬🇧 Sonia (Female, UK)',
    'en-GB-RyanNeural': '🇬🇧 Ryan (Male, UK)',
    'en-AU-NatashaNeural': '🇦🇺 Natasha (Female, AU)',

    # Spanish
    'es-ES-ElviraNeural': '🇪🇸 Elvira (Female, Spain)',
    'es-ES-AlvaroNeural': '🇪🇸 Alvaro (Male, Spain)',
    'es-MX-DaliaNeural': '🇲🇽 Dalia (Female, Mexico)',

    # French
    'fr-FR-DeniseNeural': '🇫🇷 Denise (Female)',
    'fr-FR-HenriNeural': '🇫🇷 Henri (Male)',

    # German
    'de-DE-KatjaNeural': '🇩🇪 Katja (Female)',
    'de-DE-ConradNeural': '🇩🇪 Conrad (Male)',

    # Italian
    'it-IT-ElsaNeural': '🇮🇹 Elsa (Female)',
    'it-IT-DiegoNeural': '🇮🇹 Diego (Male)',

    # Portuguese
    'pt-BR-FranciscaNeural': '🇧🇷 Francisca (Female, Brazil)',
    'pt-PT-RaquelNeural': '🇵🇹 Raquel (Female, Portugal)',

    # Russian
    'ru-RU-SvetlanaNeural': '🇷🇺 Svetlana (Female)',
    'ru-RU-DmitryNeural': '🇷🇺 Dmitry (Male)',

    # Arabic
    'ar-SA-ZariyahNeural': '🇸🇦 Zariyah (Female)',
    'ar-EG-SalmaNeural': '🇪🇬 Salma (Female, Egypt)',

    # Chinese
    'zh-CN-XiaoxiaoNeural': '🇨🇳 Xiaoxiao (Female)',
    'zh-CN-YunxiNeural': '🇨🇳 Yunxi (Male)',

    # Japanese
    'ja-JP-NanamiNeural': '🇯🇵 Nanami (Female)',
    'ja-JP-KeitaNeural': '🇯🇵 Keita (Male)',

    # Korean
    'ko-KR-SunHiNeural': '🇰🇷 SunHi (Female)',
    'ko-KR-InJoonNeural': '🇰🇷 InJoon (Male)',

    # Hindi
    'hi-IN-SwaraNeural': '🇮🇳 Swara (Female)',

    # Turkish
    'tr-TR-EmelNeural': '🇹🇷 Emel (Female)',

    # Dutch
    'nl-NL-ColetteNeural': '🇳🇱 Colette (Female)',

    # Polish
    'pl-PL-ZofiaNeural': '🇵🇱 Zofia (Female)',
}

# Store user preferences
user_settings = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    user_settings[user_id] = {'voice': 'en-US-AriaNeural'}

    await update.message.reply_text(
        '🎙️ *Welcome to Advanced TTS AI Bot!*\n\n'
        'I can convert your text to high-quality speech in 30+ languages with natural voices.\n\n'
        '*Commands:*\n'
        '/start - Start the bot\n'
        '/voice - Choose voice\n'
        '/voices - List all available voices\n'
        '/help - Get help\n\n'
        '*Usage:*\n'
        'Just send me any text and I\'ll convert it to speech!',
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    await update.message.reply_text(
        '*How to use:*\n\n'
        '1. Choose your voice with /voice\n'
        '2. Send any text message (up to 3000 characters)\n'
        '3. Receive high-quality audio file!\n\n'
        '*Features:*\n'
        '✅ 30+ natural voices\n'
        '✅ 15+ languages\n'
        '✅ Professional quality\n'
        '✅ Fast processing\n'
        '✅ MP3 format\n\n'
        '*Perfect for:*\n'
        '🎬 Content creation\n'
        '📚 Audiobooks\n'
        '🎓 Educational content\n'
        '📱 Social media videos',
        parse_mode='Markdown'
    )


async def voice_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show voice selection keyboard."""
    keyboard = []
    row = []
    for voice_id, voice_name in list(VOICES.items())[:20]:
        row.append(InlineKeyboardButton(voice_name[:25], callback_data=f"voice_{voice_id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("📋 Show All Voices", callback_data="show_all")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('🎤 *Choose your voice:*', reply_markup=reply_markup, parse_mode='Markdown')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if query.data.startswith('voice_'):
        voice_id = query.data.split('voice_')[1]
        if user_id not in user_settings:
            user_settings[user_id] = {}
        user_settings[user_id]['voice'] = voice_id
        await query.edit_message_text(
            f"✅ Voice set to *{VOICES[voice_id]}*\n\nNow send me text to convert!",
            parse_mode='Markdown'
        )
    elif query.data == "show_all":
        voice_list = "\n".join([f"• {name}" for name in VOICES.values()])
        await query.edit_message_text(
            f"*All Available Voices:*\n\n{voice_list}\n\nUse /voice to select one!",
            parse_mode='Markdown'
        )


async def generate_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate speech from text."""
    user_id = update.effective_user.id
    text = update.message.text

    if len(text) > 3000:
        await update.message.reply_text("❌ Text too long! Please send less than 3000 characters.")
        return

    # Get user voice preference
    voice = user_settings.get(user_id, {}).get('voice', 'en-US-AriaNeural')

    # Send "processing" message
    processing_msg = await update.message.reply_text("🎙️ Generating speech... Please wait.")

    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            output_path = tmp_file.name

        # Generate speech using edge-tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

        # Send audio file
        with open(output_path, 'rb') as audio:
            await update.message.reply_audio(
                audio=audio,
                title="Generated Speech",
                performer="TTS AI Bot",
                caption=f"🎧 Voice: {VOICES[voice]}\n📝 Characters: {len(text)}"
            )

        # Cleanup
        os.remove(output_path)
        await processing_msg.delete()

    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        await processing_msg.edit_text(f"❌ Error generating speech. Please try again.\nError: {str(e)}")


async def voices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all available voices."""
    voice_list = "\n".join([f"• {name}" for name in VOICES.values()])
    await update.message.reply_text(
        f"*Available Voices ({len(VOICES)}):*\n\n{voice_list}\n\n"
        f"Use /voice to select one!",
        parse_mode='Markdown'
    )


async def main():
    """Start the bot."""
    # REPLACE THIS with your bot token from BotFather
    TOKEN = "8579361468:AAHtpItEv04gCQZnLr03qHpORtAeIORgwHk"

    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("voice", voice_selection))
    application.add_handler(CommandHandler("voices", voices_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_speech))

    # Start the Bot
    print("✅ Bot is running... Keep this cell running!")
    print("⚠️ Do NOT close this notebook or the bot will stop!")

    # Initialize and start polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping bot...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


# Run the bot
if __name__ == '__main__':
    asyncio.run(main())