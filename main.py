import logging
import random
import io

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "9233906569:AAFAv3yIsJ3PrgIAFfyJWTfux3_WqPPlqTM"

logging.basicConfig(level=logging.INFO)

user_words = {}


# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "User"
    username = f"@{user.username}" if user.username else "ইউজারনেম নেই"

    await update.message.reply_text(
        f"👋 Welcome {name}!\n"
        f"(Username: {username})\n\n"
        "Send text to generate case variations."
    )


# RECEIVE TEXT
async def receive_word(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    word = update.message.text.strip()

    if not word:
        return

    if len(word) > 30:
        await update.message.reply_text(
            "❌ Maximum length is 30 characters."
        )
        return

    user_id = update.effective_user.id
    user_words[user_id] = word

    keyboard = [
        [
            InlineKeyboardButton("100", callback_data="100"),
            InlineKeyboardButton("500", callback_data="500"),
            InlineKeyboardButton("1000", callback_data="1000")
        ]
    ]

    await update.message.reply_text(
        f"✅ Text: {word}\n\n"
        "Choose the number of variations:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# MIX LETTERS
def mix_word(word):

    result = []

    for char in word:

        if char.isalpha():
            result.append(
                random.choice([char.upper(), char.lower()])
            )
        else:
            result.append(char)

    return "".join(result)


# GENERATE FILE
async def generate_words(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    word = user_words.get(user_id)

    if not word:
        await query.message.reply_text(
            "❌ Send text first."
        )
        return

    count = int(query.data)

    await query.edit_message_text(
        f"⏳ Generating {count} variations..."
    )

    results = []

    while len(results) < count:
        results.append(mix_word(word))

    # Create TXT file
    file_content = "\n".join(
        f"{i + 1}. {item}"
        for i, item in enumerate(results)
    )

    file_bytes = io.BytesIO(
        file_content.encode("utf-8")
    )

    file_bytes.name = f"variations_{count}.txt"

    # Send file
    await query.message.reply_document(
        document=file_bytes,
        filename=file_bytes.name,
        caption=f"✅ {count} variations created."
    )


# MAIN
def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_word
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            generate_words,
            pattern="^(100|500|1000)$"
        )
    )

    print("Bot is running!")

    app.run_polling()


if __name__ == "__main__":
    main()