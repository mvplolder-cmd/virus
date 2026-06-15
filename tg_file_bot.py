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

# Папки с файлами (положи сюда свои .exe и .apk)
EXE_FOLDER = "files/exe"
APK_FOLDER = "files/apk"
# =============================================

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("💻 EXE файлы"), KeyboardButton("📱 APK файлы")],
        [KeyboardButton("ℹ️ Помощь")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)


def get_files(folder: str, ext: str) -> list[str]:
    """Возвращает список файлов с нужным расширением из папки."""
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        return []
    return [
        f for f in os.listdir(folder)
        if f.lower().endswith(ext)
    ]


def build_file_keyboard(files: list[str]) -> ReplyKeyboardMarkup:
    """Строит клавиатуру из списка файлов (по 2 в ряд) + кнопка назад."""
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
        "👋 *Привет!* Я бот для отправки файлов.\n\n"
        "Выбери категорию файла на клавиатуре ниже 👇",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # --- Главное меню ---
    if text == "🔙 Главное меню":
        await update.message.reply_text(
            "Главное меню. Выбери категорию:",
            reply_markup=MAIN_KEYBOARD
        )
        return

    # --- Список EXE ---
    if text == "💻 EXE файлы":
        files = get_files(EXE_FOLDER, ".exe")
        if not files:
            await update.message.reply_text(
                "❌ В папке нет .exe файлов.\n"
                f"Положи файлы в папку `{EXE_FOLDER}/`",
                parse_mode="Markdown",
                reply_markup=MAIN_KEYBOARD
            )
            return
        context.user_data["mode"] = "exe"
        await update.message.reply_text(
            f"💻 Найдено EXE файлов: *{len(files)}*\nВыбери нужный:",
            parse_mode="Markdown",
            reply_markup=build_file_keyboard(files)
        )
        return

    # --- Список APK ---
    if text == "📱 APK файлы":
        files = get_files(APK_FOLDER, ".apk")
        if not files:
            await update.message.reply_text(
                "❌ В папке нет .apk файлов.\n"
                f"Положи файлы в папку `{APK_FOLDER}/`",
                parse_mode="Markdown",
                reply_markup=MAIN_KEYBOARD
            )
            return
        context.user_data["mode"] = "apk"
        await update.message.reply_text(
            f"📱 Найдено APK файлов: *{len(files)}*\nВыбери нужный:",
            parse_mode="Markdown",
            reply_markup=build_file_keyboard(files)
        )
        return

    # --- Помощь ---
    if text == "ℹ️ Помощь":
        await update.message.reply_text(
            "📖 *Как пользоваться ботом:*\n\n"
            "1️⃣ Нажми *💻 EXE файлы* или *📱 APK файлы*\n"
            "2️⃣ Выбери нужный файл из списка\n"
            "3️⃣ Файл придёт прямо в чат\n\n"
            "📁 *Для администратора:*\n"
            f"• EXE файлы кладите в папку `{EXE_FOLDER}/`\n"
            f"• APK файлы кладите в папку `{APK_FOLDER}/`",
            parse_mode="Markdown",
            reply_markup=MAIN_KEYBOARD
        )
        return

    # --- Отправка файла по кнопке ---
    if text.startswith("📥 "):
        filename = text[3:].strip()  # убираем "📥 "
        mode = context.user_data.get("mode", "")

        if filename.lower().endswith(".exe"):
            filepath = os.path.join(EXE_FOLDER, filename)
        elif filename.lower().endswith(".apk"):
            filepath = os.path.join(APK_FOLDER, filename)
        else:
            # определяем по текущему режиму
            if mode == "exe":
                filepath = os.path.join(EXE_FOLDER, filename)
            else:
                filepath = os.path.join(APK_FOLDER, filename)

        if not os.path.exists(filepath):
            await update.message.reply_text(
                f"❌ Файл `{filename}` не найден.",
                parse_mode="Markdown"
            )
            return

        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        await update.message.reply_text(
            f"⏳ Отправляю *{filename}* ({size_mb:.1f} МБ)...",
            parse_mode="Markdown"
        )

        try:
            with open(filepath, "rb") as f:
                await update.message.reply_document(
                    document=f,
                    filename=filename,
                    caption=f"✅ *{filename}*\n📦 Размер: {size_mb:.1f} МБ",
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Ошибка отправки файла: {e}")
            await update.message.reply_text(
                f"❌ Ошибка при отправке файла: {e}"
            )
        return

    # --- Неизвестное сообщение ---
    await update.message.reply_text(
        "Не понимаю. Используй кнопки клавиатуры 👇",
        reply_markup=MAIN_KEYBOARD
    )


def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Укажи BOT_TOKEN в начале файла!")
        print("   Получи токен у @BotFather в Telegram")
        return

    # Создаём папки если нет
    os.makedirs(EXE_FOLDER, exist_ok=True)
    os.makedirs(APK_FOLDER, exist_ok=True)

    print("🤖 Бот запускается...")
    print(f"📁 EXE папка: {os.path.abspath(EXE_FOLDER)}")
    print(f"📁 APK папка: {os.path.abspath(APK_FOLDER)}")
    print("✅ Положи файлы в эти папки и бот будет их отправлять")
    print("🛑 Остановить: Ctrl+C")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
