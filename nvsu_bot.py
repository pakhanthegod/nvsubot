import logging
import os

import telegram
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler
)

import data_handler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get('TOKEN')

FIRST, SECOND, THIRD = range(3)

updater = Updater(token=TOKEN)

data = data_handler.load_json('data1.json')
global_course_keyboard = []
global_day_keyboard = []
global_groups = {}

for course, groups in data.items():
    global_course_keyboard.append([InlineKeyboardButton(text=course, callback_data=course)])
    global_groups[course] = []
    for group, days in groups.items():
        global_groups[course].append(group)
for day, _ in days.items():
    global_day_keyboard.append([InlineKeyboardButton(text=day, callback_data=day)])

def start(bot, update, user_data):
    logging.info('Get the "/start" command')

    global global_course_keyboard

    keyboard_markup = InlineKeyboardMarkup(inline_keyboard=global_course_keyboard)

    bot.send_message(chat_id=update.message.chat_id, text="Выберите курс:", reply_markup=keyboard_markup)

    return FIRST

def get_group(bot, update, user_data):
    logging.info('Get the FIRST state')

    query = update.callback_query
    global global_groups

    user_data['course'] = query.data

    local_group_keyboard = []

    for group in global_groups[query.data]:
        local_group_keyboard.append([InlineKeyboardButton(text=group, callback_data=group)])

    keyboard_markup = InlineKeyboardMarkup(inline_keyboard=local_group_keyboard)

    bot.edit_message_text(text='Выберите группу', chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=keyboard_markup)

    return SECOND

def get_day(bot, update, user_data):
    logging.info('Get the SECOND state')

    query = update.callback_query
    global global_day_keyboard

    user_data['group'] = query.data

    keyboard_markup = InlineKeyboardMarkup(inline_keyboard=global_day_keyboard)

    bot.edit_message_text(text='Выберите день', chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=keyboard_markup)

    return THIRD

def send_table(bot, update, user_data):
    logging.info('Get the THIRD state')

    query = update.callback_query
    day = query.data
    global data
    current_data = data[user_data['course']][user_data['group']][day]
    
    answer = ''
    for time, subject in current_data.items():
        if time and subject:
            answer += f"*{time}* — _{subject}_\n"

    if not answer:
        answer = 'Нет пар'

    bot.edit_message_text(text=answer, chat_id=query.message.chat_id, message_id=query.message.message_id, parse_mode=telegram.ParseMode.MARKDOWN)

    return -1

conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start, pass_user_data=True)],
    states={
        FIRST: [CallbackQueryHandler(get_group, pass_user_data=True)],
        SECOND: [CallbackQueryHandler(get_day, pass_user_data=True)],
        THIRD: [CallbackQueryHandler(send_table, pass_user_data=True)]
    },
    fallbacks=[CommandHandler('start', start, pass_user_data=True)]
)


dispatcher = updater.dispatcher

dispatcher.add_handler(conversation_handler)

updater.start_polling()
logging.info('Bot is started!')
updater.idle()