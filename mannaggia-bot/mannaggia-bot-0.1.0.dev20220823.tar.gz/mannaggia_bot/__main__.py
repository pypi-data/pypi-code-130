#!/usr/bin/python3

"""
            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004
 Copyright (C) 2022 Christian "veeso" Visintin
 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.
            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
  0. You just DO WHAT THE FUCK YOU WANT TO.
"""

from os import environ, unlink
from random import choice
import logging
from logging import info, debug, error
from mannaggia.santi.factory import Factory as SantiFactory
from mannaggia.speech.tts import TTSError
from mannaggia.speech.google_translate import GoogleTranslateTTS
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from tempfile import NamedTemporaryFile

TELEGRAM_API_KEY = environ["TELEGRAM_API_KEY"]
PORT = int(environ.get("PORT", 0))
LOG_LEVEL = environ.get("LOG_LEVEL", "info")


def main() -> None:
    # get dictionary
    global santi
    global tts_engine
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=get_loglevel(LOG_LEVEL),
    )

    santi = SantiFactory.make_santi_from_local()
    info(f"initialized santi database with {len(santi)} entries")
    tts_engine = GoogleTranslateTTS()
    info("initialized google translate tts engine")
    updater = Updater(TELEGRAM_API_KEY, use_context=True)
    info(f"initialized telegram updater {TELEGRAM_API_KEY}")
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("mannaggia", say))
    updater.dispatcher.add_handler(CommandHandler("help", help))
    info("starting telegram bot")
    # Start the Bot
    if PORT == 0:
        info("starting bot without webhook")
        updater.start_polling()
    else:
        info("starting bot with webook")
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TELEGRAM_API_KEY,
            webhook_url="https://mannaggiapy-bot.herokuapp.com/" + TELEGRAM_API_KEY,
        )
    updater.idle()
    exit(0)


def start(update: Update, _: CallbackContext):
    update.message.reply_text(
        "Benvenuto nel mannaggia bot. Scrivi /help per vedere i comandi disponibili"
    )


def say(update: Update, context: CallbackContext):
    text = update.message.text.replace("/mannaggia", "").strip()
    debug("using espeak")
    if len(text) == 0:
        santo = choice(santi).name
    else:
        santo = text
    try:
        debug(f"getting speech for {santo}")
        audio = tts_engine.get_speech(f"mannaggia a {santo}")
    except TTSError as err:
        error(f"failed to get tts speech: {err}")
        return reply_err(update, "Il tts non funziona. Cazzo.")
    debug("correctly got the audio from tts engine")
    # writing audio to tempfile
    with NamedTemporaryFile("w+b", suffix=".ogg", delete=False) as f:
        audio.export(f.name, "ogg")
        f.close()
        debug(f"audio exported to {f.name}")
        # sending document
        debug("sending voice message...")
        context.bot.send_voice(
            chat_id=update.message.chat_id,
            voice=open(f.name, "rb"),
            duration=audio.duration_seconds,
        )
        info("audio file sent")
        unlink(f.name)
        debug("file removed")


def reply_err(update: Update, text: str):
    update.message.reply_text(text)


def help(update: Update, _: CallbackContext):
    update.message.reply_text(
        """/mannaggia - nomina un santo a caso
/mannaggia <nome> - nomina il santo inserito 
/help - mostra questo messaggio"""
    )


def get_loglevel(level: str) -> int:
    try:
        return {
            "info": logging.INFO,
            "error": logging.ERROR,
            "debug": logging.DEBUG,
            "warn": logging.WARN,
        }.get(level)
    except Exception:
        return logging.ERROR


if __name__ == "__main__":
    main()
