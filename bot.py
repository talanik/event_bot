import asyncio
import datetime
import os
import urllib

import aioschedule

import keyboards as kb

from Class.db import DB
from Class.event import EVENT
from Class.notification import NOTIFICATION
from Class.system import SYSTEM

from keyboards import contact, eventBtn, mainBtns, langBtn, cancelBtn

from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


system = SYSTEM()
authorized_ids = system.getAgents()
token = system.getToken()

langDB = DB()

notify = NOTIFICATION()

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    username = State()
    file_id = State()
    part = State()
    importer = State()
    contact = State()
    addPhoto = State()
    addDesc = State()
    addDate = State()
    addLimit = State()
    eventsetup = State()
    lang = State()


async def everyDayNotify():

    try:

        notify.remind()

    except:

        print(datetime.now(), "Ежедневное уведомление не отправлено")


async def scheduler():

    aioschedule.every().day.at("10:00").do(everyDayNotify)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(x):

    print('Run')
    asyncio.create_task(scheduler())


@dp.message_handler(lambda message: message.text in langDB.fetchone(table='localize',conditions={'alias':"cancel"},closed=False), state=Form)
async def cancel_buying(message: types.Message, state: FSMContext):

    NewTempUser = DB()

    NewTempUser.deleteRow(
        table='temp_users',
        conditions={"user_id": message.from_user.id}
    )

    await bot.send_message(message.from_user.id, "Процесс отменен", reply_markup = kb.start_markup)
    await state.finish()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message, state: FSMContext):
    authorized_ids = system.getAgents()

    btns_main = mainBtns(lang=message.from_user.id)

    if authorized_ids.get(message.from_user.id) is None:

        try:
            newUsersDB = DB()

            res = newUsersDB.fetchone(
                table='users',
                conditions={"user_id": message.from_user.id},
                closed=False
            )

            if res is None:

                await message.answer(
                    text=system.getlocalize(user_id=message.from_user.id, alias='choose_lang'),
                    reply_markup = kb.reg_lang_markup
                )

                await Form.lang.set()

            else:

                await bot.send_message(
                    chat_id=message.chat.id,
                    text=system.getlocalize(user_id=message.from_user.id,alias='start_text'),
                    reply_markup=btns_main
                )
        except:
            await message.answer(
                text=system.getlocalize(user_id=message.from_user.id, alias='choose_lang'),
                reply_markup=kb.reg_lang_markup
            )

            await Form.lang.set()


    else:

        await bot.send_message(
            chat_id=message.chat.id,
            text=f'''Приветствую {authorized_ids.get(message.from_user.id)}!''',
            reply_markup=btns_main
        )


@dp.message_handler(lambda message: message.text in langDB.fetchone(table='localize',conditions={'alias':"events"},closed=False))
async def process_events_command(message: types.Message):
    authorized_ids = system.getAgents()

    allEvents = EVENT()

    if authorized_ids.get(message.from_user.id) is not None:

        allEvents.events(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            token = token
        )

    else:

        allEvents.events(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            token = token,
            poll='user'
        )


@dp.message_handler(lambda message: message.text in langDB.fetchone(table='localize',conditions={'alias':"my_events"},closed=False))
async def process_events_command(message: types.Message):
    authorized_ids = system.getAgents()

    allEvents = EVENT()

    if authorized_ids.get(message.from_user.id) is not None:

        allEvents.myEvents(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            token = token
        )

    else:

        allEvents.myEvents(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            token = token,
            poll='user'
        )


@dp.message_handler(lambda message: message.text in langDB.fetchone(table='localize',conditions={'alias':"language"},closed=False))
async def lang_command(message: types.Message):

    await bot.send_message(
        chat_id=message.from_user.id,
        text=system.getlocalize(alias='language',user_id=message.from_user.id),
        reply_markup=langBtn(user_id=message.from_user.id)
    )


@dp.callback_query_handler(text_contains="langauage")
async def changeLang(call: types.CallbackQuery):

    await call.answer(cache_time=1)

    checkedLang = call.data
    checkedLang = checkedLang.split('::')

    if checkedLang[1]!="cancel":

        langChange = DB()

        langChange.update(
            table='users',
            sets={"lang": checkedLang[1]},
            conditions={'user_id': call.from_user.id}
        )

        btns_main = mainBtns(lang=call.from_user.id)

        await bot.send_message(
            chat_id=call.message.chat.id,
            text=system.getlocalize(alias='not_lang_change',user_id=call.from_user.id),
            reply_markup=btns_main
        )

    await bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )


@dp.callback_query_handler(text_contains="publication")
async def toOrder(call: types.CallbackQuery):

    eventEx = EVENT()

    await call.answer(cache_time=1)

    current_event = call.data
    current_event = current_event.split('::')
    event_id = current_event[0]

    res = eventEx.publication(event_id=event_id)

    notify.newEvent(res[0])

    await bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=res[1],
        reply_markup=eventBtn(res, 'admin', False)
    )


@dp.callback_query_handler(text_contains="subscribe")
async def subscribe(call: types.CallbackQuery):

    eventEx = EVENT()

    await call.answer(cache_time=1)

    current_event = call.data
    current_event = current_event.split('::')
    event_id = current_event[0]

    res = eventEx.subscribe(event_id=event_id, user_id=call.from_user.id)

    await bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=res[1],
        reply_markup=eventBtn(res, 'user', False)
    )

    await bot.send_message(
        chat_id=call.message.chat.id,
        text=system.getlocalize(user_id=call.from_user.id, alias="not_subscribe"),
        reply_markup=mainBtns(lang=call.from_user.id)
    )


@dp.callback_query_handler(text_contains="subscribs")
async def subscribe(call: types.CallbackQuery):

    await call.answer(cache_time=1)
    try:
        user_id = call.from_user.id
        current_event = call.data
        current_event = current_event.split('::')
        event_id = current_event[0]

        subscribeDB =DB()

        event_name = subscribeDB.fetchone(
            table="events",
            columns=['event_name'],
            conditions={"event_id": event_id}
        )

        file = system.getSubscribers(event_id)
        filename = open(file, "rb")

        await bot.send_document(user_id, filename, caption=f'Подписчики на событие "{event_name[0]}" (ID: {event_id})')

        os.remove(f'{file}')

    except:

        await bot.send_message(
            chat_id=call.message.chat.id,
            text="Что то пошло не так",
            reply_markup=mainBtns(lang=call.from_user.id)
        )

@dp.message_handler(state=Form.lang)
async def cancel_buying(message: types.Message, state: FSMContext):

    if message.text=='RU' or message.text=='UZ':

        NewTempUser = DB()

        NewTempUser.insert(
            table='temp_users',
            columns=['user_id','lang','chat_id'],
            values=[message.from_user.id,message.text,message.chat.id]
        )

        await state.finish()

        await message.answer(system.getReglocalize(user_id=message.from_user.id, alias='add_name'), reply_markup = cancelBtn(user_id=message.from_user.id))

        await Form.username.set()

    else:

        await message.answer(system.getReglocalize(user_id=message.from_user.id, alias='choose_lang'), reply_markup = kb.reg_lang_markup)


@dp.message_handler(state=Form.username)
async def cancel_buying(message: types.Message, state: FSMContext):

    txt = list(message.text)

    if txt[0]!='/' and len(txt)>0 and len(list(message.text.replace(" ","")))>0:

        NewTempUser = DB()

        NewTempUser.update(
            table='temp_users',
            sets={'user_name': message.text},
            conditions={"user_id": message.from_user.id}
        )

        await state.finish()

        btn = contact(lang=message.from_user.id)

        await bot.send_message(
            chat_id=message.chat.id,
            text=system.getReglocalize(user_id=message.from_user.id, alias='add_phone'),
            reply_markup=btn
        )

        await Form.contact.set()

    else:

        await message.answer(system.getReglocalize(user_id=message.from_user.id, alias='add_name'), reply_markup = cancelBtn(user_id=message.from_user.id))


@dp.message_handler(content_types=['contact'], state=Form.contact)
async def add_agents(message: types.Message, state: FSMContext):
    contact_num = message.contact

    NewTempUser = DB()

    NewTempUser.update(
        table='temp_users',
        sets={'phone': contact_num['phone_number']},
        conditions={"user_id": message.from_user.id}
    )

    await state.finish()

    await bot.send_message(
        chat_id=message.chat.id,
        text=system.getReglocalize(user_id=message.from_user.id, alias='add_part'),
        reply_markup = cancelBtn(user_id=message.from_user.id))

    await Form.part.set()


@dp.message_handler(state=Form.contact)
async def cancel_buying(message: types.Message, state: FSMContext):
    txt = list(message.text)
    number_phone = message.text

    if number_phone[:5]=='+9989' and len(list(number_phone))>12 and txt[0]!='/':

        NewTempUser = DB()

        NewTempUser.update(
            table='temp_users',
            sets={'phone': number_phone},
            conditions={"user_id": message.from_user.id}
        )

        await state.finish()

        await bot.send_message(
            chat_id=message.chat.id,
            text=system.getReglocalize(user_id=message.from_user.id, alias='add_part'),
            reply_markup=cancelBtn(user_id=message.from_user.id))

        await Form.part.set()

    else:

        btn = contact(lang=message.from_user.id)

        await bot.send_message(
            chat_id=message.chat.id,
            text=system.getReglocalize(user_id=message.from_user.id, alias='add_phone'),
            reply_markup=btn
        )


@dp.message_handler(state=Form.part)
async def cancel_buying(message: types.Message, state: FSMContext):

    txt = list(message.text)

    if txt[0]!='/' and len(txt)>0:

        NewTempUser = DB()

        NewTempUser.update(
            table='temp_users',
            sets={'edu': message.text},
            conditions={"user_id": message.from_user.id},
            closed=False
        )

        user = NewTempUser.fetchone(
            table='temp_users',
            conditions={"user_id": message.from_user.id},
            closed=False
        )

        cols = NewTempUser.getColumns(table='users')

        NewTempUser.insert(
            table='users',
            columns=cols,
            values=user,
            closed=False
        )

        NewTempUser.deleteRow(table='temp_users',conditions={'user_id': message.from_user.id})

        btns_main = mainBtns(lang=message.from_user.id)

        await state.finish()

        await bot.send_message(
            chat_id=message.chat.id,
            text=system.getlocalize(user_id=message.from_user.id,alias='start_text'),
            reply_markup=btns_main
        )

    else:

        await bot.send_message(
            chat_id=message.chat.id,
            text=system.getReglocalize(user_id=message.from_user.id, alias='add_part'),
            reply_markup=cancelBtn(user_id=message.from_user.id)
        )


@dp.message_handler(commands=['id'])
async def process_start_command(message: types.Message):
    await message.answer(f"Ваш ID: {message.from_user.id}")


@dp.message_handler(lambda message: message.text in langDB.fetchone(table='localize',conditions={'alias':"help"},closed=False))
async def process_help_command(message: types.Message):
    authorized_ids = system.getAgents()

    main = mainBtns(lang=message.from_user.id)

    if (authorized_ids.get(message.from_user.id) is None):

        await message.answer(f'''Доступные команды
        /id - узнайте свой Telegram ID''', reply_markup=main)

    else:

        await message.answer(f'''Доступные команды
        /id - узнайте свой Telegram ID
        /importToTable - Добавить или удалить администраторов
        /getTplAgents - Получить шаблон файла для работы с администраторами
        /getTplEvents - Получить шаблон файла для работы с событиями
        ''', reply_markup=main)


@dp.message_handler(commands=['importToTable'])
async def start_adding_agents(message: types.Message):
    authorized_ids = system.getAgents()

    if (authorized_ids.get(message.from_user.id) is None):

        await message.answer("Вы не авторизованы.")

    else:

        await Form.importer.set()

        text = f"Загрузите файл импорта для добавления или удаления сотрудников" \
               f"\n" \
               f"Загружаемый файл должен быть в расширении .xls или .xlsx" \
               f"\n" \
               f"Пожалуйста, загрузите файл для добавления сотрудников Вашего отдела"

        await message.reply(text=text, reply_markup=cancelBtn(user_id=message.from_user.id))


@dp.message_handler(content_types=['document'], state=Form.importer)
async def add_agents(message: types.Message, state: FSMContext):

    try:

        main_reply = mainBtns(lang=message.from_user.id)

        document_id = message.document.file_id
        file_info = await bot.get_file(document_id)
        fi = file_info.file_path
        name = message.document.file_name
        urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{token}/{fi}', f'./{name}')

        newSetup = SYSTEM()
        newSetup.importToTable(file=name)

        await bot.send_message(message.from_user.id, 'Файл успешно сохранён', reply_markup=main_reply)

        await state.finish()

    except Exception as e:

        await bot.send_message(message.from_user.id, 'Что-то пошло не так. Проверьте, пожалуйста, файл', reply_markup=main_reply)


@dp.message_handler(commands=['getTplAgents'])
async def process_file_command(message: types.Message):
    user_id = message.from_user.id
    filename = open(f"tpl/import_agent.xlsx", "rb")
    await bot.send_document(user_id, filename,
                            caption='Файл для работы со списком сотрудников')


@dp.message_handler(commands=['getTplEvents'])
async def process_file_command(message: types.Message):
    user_id = message.from_user.id
    filename = open(f"tpl/import_events.xlsx", "rb")
    await bot.send_document(user_id, filename,
                            caption='Файл для работы со списком событий')


@dp.message_handler(commands=['getTplLocalize'])
async def process_file_command(message: types.Message):
    user_id = message.from_user.id
    filename = open(f"tpl/import_localize.xlsx", "rb")
    await bot.send_document(user_id, filename,
                            caption='Файл для работы со списком локализаций')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)