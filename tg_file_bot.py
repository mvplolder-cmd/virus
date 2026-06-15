import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =============================================
# НАСТРОЙКИ — замени на свои значения
# =============================================
BOT_TOKEN = "8732875693:AAEQ_To_tEYQYvxUFGvPtT54JFAHypztVfE"   # Получи у @BotFather

# Папки с файлами
EXE_FOLDER = "files/exe"
APK_FOLDER = "files/apk"
TXT_FOLDER = "files/txt"

# ПРОКСИ — раскомментируй нужный вариант и укажи свои данные:
#
# Вариант 1: SOCKS5 (например Tor Browser — запусти его и используй порт 9150)
# PROXY_URL = "socks5://127.0.0.1:9150"
#
# Вариант 2: SOCKS5 с логином/паролем
# PROXY_URL = "socks5://user:password@ip:port"
#
# Вариант 3: HTTP прокси
# PROXY_URL = "http://ip:port"
#
# Вариант 4: Без прокси (если Telegram не заблокирован)
PROXY_URL = None
# =============================================

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("💻 EXE файлы"), KeyboardButton("📱 APK файлы")],
        [KeyboardButton("📄 TXT файлы")],
        [KeyboardButton("ℹ️ Помощь")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)


def get_files(folder: str, ext: str) -> list[str]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        return []
    return [f for f in os.listdir(folder) if f.lower().endswith(ext)]


def build_file_keyboard(files: list[str]) -> ReplyKeyboardMarkup:
    buttons = []
    for i in range(0, len(files), 2):
        row = [KeyboardButton(f"📥 {files[i]}")]
        if i + 1 < len(files):
            row.append(KeyboardButton(f"📥 {files[i + 1]}"))
        buttons.append(row)
    buttons.append([KeyboardButton("🔙 Главное меню")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Привет!* Я бот для отправки файлов.\n\nВыбери категорию на клавиатуре 👇",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🔙 Главное меню":
        await update.message.reply_text("Главное меню:", reply_markup=MAIN_KEYBOARD)
        return

    if text == "💻 EXE файлы":
        files = get_files(EXE_FOLDER, ".exe")
        if not files:
            await update.message.reply_text(
                f"❌ Нет .exe файлов.\nПоложи их в папку `{EXE_FOLDER}/`",
                parse_mode="Markdown", reply_markup=MAIN_KEYBOARD
            )
            return
        context.user_data["mode"] = "exe"
        await update.message.reply_text(
            f"💻 EXE файлов: *{len(files)}*\nВыбери нужный:",
            parse_mode="Markdown", reply_markup=build_file_keyboard(files)
        )
        return

    if text == "📱 APK файлы":
        files = get_files(APK_FOLDER, ".apk")
        if not files:
            await update.message.reply_text(
                f"❌ Нет .apk файлов.\nПоложи их в папку `{APK_FOLDER}/`",
                parse_mode="Markdown", reply_markup=MAIN_KEYBOARD
            )
            return
        context.user_data["mode"] = "apk"
        await update.message.reply_text(
            f"📱 APK файлов: *{len(files)}*\nВыбери нужный:",
            parse_mode="Markdown", reply_markup=build_file_keyboard(files)
        )
        return

    if text == "📄 TXT файлы":
        files = get_files(TXT_FOLDER, ".txt")
        if not files:
            await update.message.reply_text(
                f"❌ Нет .txt файлов.\nПоложи их в папку `{TXT_FOLDER}/`",
                parse_mode="Markdown", reply_markup=MAIN_KEYBOARD
            )
            return
        context.user_data["mode"] = "txt"
        await update.message.reply_text(
            f"📄 TXT файлов: *{len(files)}*\nВыбери нужный:",
            parse_mode="Markdown", reply_markup=build_file_keyboard(files)
        )
        return

    if text == "ℹ️ Помощь":
        await update.message.reply_text(
            "📖 *Как пользоваться:*\n\n"
            "1️⃣ Выбери категорию файла\n"
            "2️⃣ Выбери файл из списка\n"
            "3️⃣ Файл придёт прямо в чат\n\n"
            f"📁 EXE → папка `{EXE_FOLDER}/`\n"
            f"📁 APK → папка `{APK_FOLDER}/`\n"
            f"📁 TXT → папка `{TXT_FOLDER}/`",
            parse_mode="Markdown", reply_markup=MAIN_KEYBOARD
        )
        return

    if text.startswith("📥 "):
        filename = text[3:].strip()
        mode = context.user_data.get("mode", "")

        if filename.lower().endswith(".exe"):
            filepath = os.path.join(EXE_FOLDER, filename)
        elif filename.lower().endswith(".apk"):
            filepath = os.path.join(APK_FOLDER, filename)
        elif filename.lower().endswith(".txt"):
            filepath = os.path.join(TXT_FOLDER, filename)
        else:
            folder_map = {"exe": EXE_FOLDER, "apk": APK_FOLDER, "txt": TXT_FOLDER}
            filepath = os.path.join(folder_map.get(mode, EXE_FOLDER), filename)

        if not os.path.exists(filepath):
            await update.message.reply_text(f"❌ Файл `{filename}` не найден.", parse_mode="Markdown")
            return

        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        await update.message.reply_text(f"⏳ Отправляю *{filename}* ({size_mb:.1f} МБ)...", parse_mode="Markdown")

        try:
            with open(filepath, "rb") as f:
                await update.message.reply_document(
                    document=f,
                    filename=filename,
                    caption=f"✅ *{filename}*\n📦 {size_mb:.1f} МБ",
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Ошибка отправки: {e}")
            await update.message.reply_text(f"❌ Ошибка: {e}")
        return

    await update.message.reply_text("Используй кнопки клавиатуры (примечание то что у файлов убрана одна буква на пример не Petya.exe а etya.exe) 👇", reply_markup=MAIN_KEYBOARD)


def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Укажи BOT_TOKEN в начале файла!")
        return

    os.makedirs(EXE_FOLDER, exist_ok=True)
    os.makedirs(APK_FOLDER, exist_ok=True)
    os.makedirs(TXT_FOLDER, exist_ok=True)

    print("🤖 Бот запускается...")
    print(f"📁 EXE: {os.path.abspath(EXE_FOLDER)}")
    print(f"📁 APK: {os.path.abspath(APK_FOLDER)}")

    builder = Application.builder().token(BOT_TOKEN)

    if PROXY_URL:
        print(f"🔒 Прокси: {PROXY_URL}")
        # Поддержка SOCKS5 требует: pip install httpx[socks]
        builder = builder.proxy(PROXY_URL).get_updates_proxy(PROXY_URL)
    else:
        print("⚠️  Прокси не настроен. Если Telegram заблокирован — укажи PROXY_URL в файле.")

    print("✅ Готово! Бот работает. Остановить: Ctrl+C\n")

    app = builder.build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
