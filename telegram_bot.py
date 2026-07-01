import os
from telegram import Update
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from ai_logic import generate_answer, initialize_client, analyze_pdf
from telegram.constants import ParseMode

load_dotenv()
initialize_client()
telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")

# Persiapkan format mention (@username) dengan aman
raw_username = os.environ.get("TELEGRAM_BOT_USERNAME", "")
bot_username = raw_username.replace("@", "")
bot_mention = f"@{bot_username}"

# --- Commands ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Halo! Aku adalah EduAssistAI, asisten virtual yang siap membantu kamu! Silakan ketik sesuatu untuk memulai percakapan.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am a banana! Please type something so I can respond!')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command!')

# --- Responses ---

def handle_response(text: str) -> str:
    processed: str = text.lower()
    generated_response = generate_answer(processed)
    
    # Penanganan jika output berupa object (genai) atau string biasa
    try:
        return generated_response.text
    except AttributeError:
        return str(generated_response)

def format_for_telegram(text: str) -> str:
    # Ubah Bold Gemini (**) menjadi Bold Telegram (*)
    formatted_text = text.replace('**', '*')
    
    # Hapus simbol Heading (#)
    formatted_text = formatted_text.replace('### ', '')
    formatted_text = formatted_text.replace('## ', '')
    formatted_text = formatted_text.replace('# ', '')
    
    return formatted_text

# --- Main Message Handler ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    
    # 1. PENANGANAN DOKUMEN PDF
    if update.message.document:
        document = update.message.document
        
        if document.mime_type == 'application/pdf':
            await update.message.reply_text("📄 PDF diterima. Sebentar, aku baca dan analisis dulu ya...")
            
            telegram_file = await context.bot.get_file(document.file_id)
            local_file_path = f"temp_{document.file_name}"
            
            await telegram_file.download_to_drive(local_file_path)
            
            user_prompt = update.message.caption if update.message.caption else "Tolong buatkan ringkasan dari dokumen ini."
            
            # Lempar ke ai_logic
            response_text = analyze_pdf(local_file_path, user_prompt)
            
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
                
            pesan_rapi = format_for_telegram(response_text)
            
            try:
                await update.message.reply_text(pesan_rapi, parse_mode=ParseMode.MARKDOWN)
            except Exception:
                await update.message.reply_text(pesan_rapi)
            
            return # Hentikan fungsi di sini agar teks tidak dobel proses

    # 2. PENANGANAN TEKS BIASA
    if not update.message.text:
        return

    text: str = update.message.text
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    response: str = ""

    # PERBAIKAN: Gunakan list untuk mengecek group maupun supergroup
    if message_type in ['group', 'supergroup']:
        # PERBAIKAN: Cek spesifik menggunakan @username
        if bot_mention in text:
            print("Group chat detected.")
            new_text: str = text.replace(bot_mention, '').strip()
            response = handle_response(new_text)
        else:
            return # Keluar dari fungsi jika bot tidak di-tag di grup
    elif message_type == 'private':
        print("Private chat detected.")
        response = handle_response(text)
    else:
        return

    # 3. PENGIRIMAN BALASAN
    if response:
        print('Bot:', response)
        pesan_rapi = format_for_telegram(response)
        
        # Menggunakan try-except karena Markdown Telegram sangat ketat
        # Jika AI mengirim simbol bintang/garis bawah yang ganjil, Telegram bisa crash
        try:
            await update.message.reply_text(pesan_rapi, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(f"Format Markdown gagal, mengirim plain text... ({e})")
            await update.message.reply_text(pesan_rapi)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    app = Application.builder().token(telegram_bot_token).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.PDF, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)