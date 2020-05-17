from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from imgurpython import ImgurClient
import pandas as pd
import configparser
import random
import time
import cv2
import os
import img_process
import TG_handler

# Load data from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')
TG_access_token = config['TELEGRAM']['TG_access_token']
imgur_client_id = config['IMGUR']['imgur_client_id']
imgur_client_secret = config['IMGUR']['imgur_client_secret']
imgur_album_id = config['IMGUR']['imgur_album_id']
imgur_access_token = config['IMGUR']['imgur_access_token']
imgur_refresh_token = config['IMGUR']['imgur_refresh_token']

TYPING_TITLE, SEARCH_SHEET, SCORE_RESULT, SEARCH_HANDLER_2, SONG_LIST_RESULT, SEARCH_SHEET_ = range(6)


updater = Updater(TG_access_token)

def cancel(bot, update):
    print('stop')

def button(update, context):
    query = update.callback_query

    query.edit_message_text(text="Selected option: {}".format(query.data))

#圖片input處理
conv_handler_sheet = ConversationHandler(
    entry_points=[MessageHandler(Filters.document, TG_handler.image_handler)],
    states={
        TYPING_TITLE: [MessageHandler(Filters.text, TG_handler.handle_title)]
        },
    fallbacks=[CommandHandler('cancel', cancel)]
)

# #/search功能
# conv_handler_search_sheet = ConversationHandler(
#     entry_points=[CommandHandler('search', TG_handler.search_sheet_handler)],
#     states={
#         SEARCH_SHEET: [MessageHandler(Filters.text, TG_handler.search_sheet)]
#         },
#     fallbacks=[CommandHandler('cancel', cancel)]
# )

# conv_handler_score = ConversationHandler(
#     entry_points=[CommandHandler('score', TG_handler.score_handler)],
#     states={
#         SCORE_RESULT: [MessageHandler(Filters.text, TG_handler.score_result)]
#         },
#     fallbacks=[CommandHandler('cancel', cancel)]
# )

#start
conv_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text, TG_handler.search_handler)],
    states={
        # SEARCH_HANDLER_2: [MessageHandler(Filters.text, TG_handler.search_handler_2)],
        SEARCH_SHEET: [MessageHandler(Filters.text, TG_handler.search_sheet)],
        SCORE_RESULT: [MessageHandler(Filters.text, TG_handler.score_result)],
        # SONG_LIST_RESULT: [TG_handler.song_list]
        },
    fallbacks=[CommandHandler('cancel', cancel)]
)

updater.dispatcher.add_handler(conv_handler_sheet)
# updater.dispatcher.add_handler(conv_handler_search_sheet)
updater.dispatcher.add_handler(conv_handler)
updater.dispatcher.add_handler(CommandHandler('start', TG_handler.start))
updater.dispatcher.add_handler(CommandHandler('song_list', TG_handler.song_list))
# updater.dispatcher.add_handler(MessageHandler(Filters.document, image_handler))

updater.dispatcher.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()