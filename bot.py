import logging
import os
import random

from telegram import (
    Update,
    ParseMode,
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultPhoto,
)
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    InlineQueryHandler,
)

from scraper import scrape_zlib

updater = Updater(token=os.environ.get("TELEGRAM_TOKEN"), use_context=True)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)
WELCOME_TEXT = "Hey *{}*!🙃\n\nEasily source for books 📚 at your comfort 🛀. \n\n🏃‍♂️🏃‍♂️🏃‍♂ Byeee! Start searching"
BOOK_RESPONSE = "`Title: {}`\n\n`Author(s): {}`\n\n`Size: {}`"


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        text=WELCOME_TEXT.format(update.effective_user.first_name),
        parse_mode=ParseMode.MARKDOWN,
    )


def search(update: Update, context: CallbackContext):
    update.message.reply_text(
        reply_markup=ForceReply(selective=True),
        text="What book do you want to search for 🤔?",
    )


# Send search confirmation
def echo(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="Search for *{}* 🧐?".format(update.message.text),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Yes", callback_data="1, {}".format(update.message.text)
                    ),
                    InlineKeyboardButton("No", callback_data="0"),
                ],
            ]
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


# Handle search confirmation
def button(update: Update, context: CallbackContext):
    query: CallbackQuery = update.callback_query

    query.answer()
    if query.data != "0":
        try:
            results = scrape_zlib(query.data.split(", ")[-1].strip())
        except:
            query.edit_message_text(text="Ooops! An error occurred ☹.️")
        else:
            if len(results) == 0:
                query.edit_message_text(
                    text="No result(s) found for *{}* 😔".format(
                        query.data.split(", ")[-1].strip()
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                query.edit_message_text(
                    text="🤗 `Result(s)` `for` *{}*".format(
                        query.data.split(", ")[-1].strip()
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                )
                # add pagination later
                for item in results[:15]:
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=item["image"],
                        caption=BOOK_RESPONSE.format(
                            item["title"], item["authors"], item["size"]
                        ),
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("More Info", url=item["url"])]]
                        ),
                        parse_mode=ParseMode.MARKDOWN,
                    )
    else:
        query.edit_message_text(text="Okay 😑.")


# inline search
def inline_search(update: Update, context: CallbackContext):
    query_response = []
    query = update.inline_query.query
    try:
        results = scrape_zlib(query)
    except:
        update.inline_query.answer(
            [
                InlineQueryResultArticle(
                    id=str(random.randint(1, 100)),
                    title="error",
                    description="Ooops! An error occurred ☹.️",
                    input_message_content=InputTextMessageContent(
                        "Ooops! An error occurred ☹.️"
                    ),
                )
            ]
        )
    else:
        if len(results) == 0:
            update.inline_query.answer(
                [
                    InlineQueryResultArticle(
                        id=str(random.randint(1, 100)),
                        title="error",
                        description="No result(s) found for *{}* 😔".format(query),
                        input_message_content=InputTextMessageContent(
                            "No result(s) found for *{}* 😔".format(query),
                            parse_mode=ParseMode.MARKDOWN,
                        ),
                    )
                ]
            )

        else:
            for index, item in enumerate(results):
                query_response.append(
                    InlineQueryResultPhoto(
                        str(index),
                        photo_url=item["image"],
                        thumb_url=item["image"],
                        caption=BOOK_RESPONSE.format(
                            item["title"], item["authors"], item["size"]
                        ),
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("More Info", url=item["url"])]]
                        ),
                    )
                )
    update.inline_query.answer(query_response)


# handle unknown commands
def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(text="Please type a language I understand 😪.")


def contact(update: Update, context: CallbackContext):
    context.bot.send_message(
        update.effective_chat.id,
        "Reach me on:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Twitter", url="https://twitter.com/_peratzatha"
                    )
                ],
            ]
        ),
    )


# error handler
def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("search", search))
updater.dispatcher.add_handler(CommandHandler("contact", contact))
updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.dispatcher.add_handler(InlineQueryHandler(inline_search))
updater.dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))
updater.dispatcher.add_error_handler(error)

if __name__ == "__main__":
    updater.start_polling()
    updater.idle()
