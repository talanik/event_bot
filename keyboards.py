from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from Class.db import DB
from Class.system import SYSTEM


def mainBtns(lang):
    mainButtons = SYSTEM()

    events_button = KeyboardButton(mainButtons.getlocalize(user_id=lang, alias='events'))
    my_events_button = KeyboardButton(mainButtons.getlocalize(user_id=lang, alias='my_events'))
    help_button = KeyboardButton(mainButtons.getlocalize(user_id=lang, alias='help'))
    lang_button = KeyboardButton(mainButtons.getlocalize(user_id=lang, alias='language'))


    main_buttons = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
        .add(events_button,my_events_button).add(help_button, lang_button)

    return main_buttons

def cancelBtn(user_id):
    cancelLang = SYSTEM()

    agents = cancelLang.getAgents()
    if user_id in agents:
        cancel_button = KeyboardButton('Отмена')
    else:
        cancel_button = KeyboardButton(cancelLang.getReglocalize(user_id=user_id,alias='cancel'))
    cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
        .add(cancel_button)

    return cancel_markup

ru_button = KeyboardButton('RU')
uz_button = KeyboardButton('UZ')
reg_lang_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
    .add(ru_button,uz_button)


def langBtn(user_id):
    cancelLang = SYSTEM()

    lang_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("RU", callback_data=f"langauage::ru"), InlineKeyboardButton("UZ", callback_data=f"langauage::uz")],
        [InlineKeyboardButton(cancelLang.getlocalize(user_id=user_id,alias='cancel'), callback_data=f"langauage::cancel")]
    ])

    return lang_markup


cancel_button = KeyboardButton('/start')
start_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
    .add(cancel_button)


def contact(lang):

    Buttons = SYSTEM()

    contact_button = KeyboardButton(Buttons.getReglocalize(user_id=lang, alias='send_contact'), request_contact=True)
    cancel_button = KeyboardButton(Buttons.getReglocalize(user_id=lang, alias='cancel'))
    contact_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) \
        .add(contact_button,cancel_button)
    return contact_markup


def eventBtn(alias, type, ordered, user_id=None):

    system = SYSTEM()

    btns = []
    b= []
    if type=='admin':
        if alias[-1]==0:
            btns.append([InlineKeyboardButton("Опубликовать", callback_data=f"{alias[0]}::publication")])
        else:
            count = system.getScribeCounts(alias[0])
            btns.append([InlineKeyboardButton(f"Подписчики ({count})", callback_data=f"{alias[0]}::subscribs")])
    elif type=='user':
        if ordered is True:
            if user_id is not None:
                event_text = system.getlocalize(user_id=user_id, alias="scribe_btn")
            else:
                event_text = "Записаться"

            btns.append([InlineKeyboardButton(event_text, callback_data=f"{alias[0]}::subscribe")])

    btns.append(b)
    btns_markup = InlineKeyboardMarkup(inline_keyboard=btns)

    return btns_markup