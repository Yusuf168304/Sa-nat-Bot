import os
import io
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from PIL import Image
from rembg import remove  # Удаление фона

TOKEN = "7325704022:AAGlL7eeSLQtZzlSNWMW5XtjB4T2MwKE4Gk"  # Замени на свой токен
STICKERS_FOLDER = "stickers"
VIDEOS_FOLDER = "videos"

# Создаём папки, если их нет
os.makedirs(STICKERS_FOLDER, exist_ok=True)
os.makedirs(VIDEOS_FOLDER, exist_ok=True)

async def start(update: Update, context):
    text = "👋 Assalomu alaykum! Men stiker yaratish va video yuklash uchun botman!\n\n" \
           "📂 Papkalar yaratish\n🖼 Stiker yasash\n🎥 Video yuklash\n⚙️ Sozlamalar\n\n" \
           "Tanlang!"
    keyboard = [
        [InlineKeyboardButton("📂 Papka yaratish", callback_data="create_folder")],
        [InlineKeyboardButton("🖼 Stiker yasash", callback_data="make_sticker")],
        [InlineKeyboardButton("🎥 Video yuklash", callback_data="download_video")],
        [InlineKeyboardButton("📁 Mening papkalarim", callback_data="view_folders")],
        [InlineKeyboardButton("⚙️ Sozlamalar", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "create_folder":
        folder_name = "sticker_papka_1"
        os.makedirs(os.path.join(STICKERS_FOLDER, folder_name), exist_ok=True)
        await query.edit_message_text(f"✅ Papka yaratildi: {folder_name}")

    elif query.data == "make_sticker":
        keyboard = [
            [InlineKeyboardButton("✅ Fonni olib tashlash", callback_data="remove_bg")],
            [InlineKeyboardButton("❌ Fonni qoldirish", callback_data="keep_bg")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Stiker qanday bo'lishini hohlaysiz:", reply_markup=reply_markup)
    
    elif query.data in ["remove_bg", "keep_bg"]:
        context.user_data["remove_bg"] = (query.data == "remove_bg")
        await query.edit_message_text("Endi menga rasm yuboring.")

    elif query.data == "download_video":
        await query.edit_message_text("🎥 Video yuklash uchun menga havolani yuboring!")

async def handle_photo(update: Update, context):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    img_stream = io.BytesIO()
    await file.download_to_memory(img_stream)
    img_stream.seek(0)

    img = Image.open(img_stream).convert("RGBA")
    img = img.resize((512, 512))

    if context.user_data.get("remove_bg", False):
        img = remove(img)

    sticker_path = os.path.join(STICKERS_FOLDER, "sticker.webp")
    img.save(sticker_path, format="WEBP")

    with open(sticker_path, "rb") as sticker:
        await update.message.reply_sticker(sticker=sticker)
    
    await update.message.reply_text("✅ Stiker tayyor!")

async def handle_video_download(update: Update, context):
    url = update.message.text.strip()
    await update.message.reply_text("📥 Yuklab olinmoqda, biroz kuting...")
    
    video_path = os.path.join(VIDEOS_FOLDER, "downloaded_video.mp4")
    
    ydl_opts = {
        "format": "best",
        "outtmpl": video_path,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open(video_path, "rb") as video:
            await update.message.reply_video(video=video)
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

async def settings(update: Update, context):
    await update.message.reply_text("⚙️ Sozlamalar: Bu yerda botni o'chirish imkoniyati bo'ladi")

async def view_folders(update: Update, context):
    folders = os.listdir(STICKERS_FOLDER)
    if not folders:
        await update.message.reply_text("❌ Sizda hali papkalar yo'q.")
    else:
        await update.message.reply_text("📁 Sizning papkalaringiz:\n" + "\n".join(folders))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video_download))
    app.add_handler(CommandHandler("settings", settings))
    app.add_handler(CommandHandler("view_folders", view_folders))
    
    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
