import time
import datetime
import requests
import locale

from Class.system import SYSTEM
from keyboards import eventBtn, mainBtns

from Class.db import DB

class EVENT():
    """Work with events"""

    def __init__(self):
        """Initsialition events"""
        self.db = DB()
        self.system = SYSTEM()

    def eventQuery(self,event_id=None, poll='admin'):

        conditions = {}
        current_time = time.time()
        if event_id is not None:
            conditions['event_id'] = event_id

        conditions['event_date'] = {}
        conditions['event_date'][0] = int(current_time)
        conditions['event_date'][1] = '>'

        if poll == 'user':
            conditions['sended'] = 1

        return conditions


    def events(self, chat_id, user_id, token, poll='admin'):

        events = self.db.fetchall(
            table='events',
            conditions=self.eventQuery(poll=poll),
            closed=False
        )

        lang = self.system.getLang(user_id=user_id)
        eventDescLang = self.system.getEventDescLang(user_id=user_id)

        text = ''

        columns = self.db.getColumns('events')

        locale.setlocale(locale.LC_ALL, f"{lang.lower()}_{lang}")
        eventDescription = columns.index(f"event_desc{eventDescLang}")

        main = mainBtns(lang=user_id)

        if len(events)>0:
            event_text = self.system.getlocalize(user_id=user_id, alias="events")
            requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={event_text}&reply_markup={main}")

            for event in events:
                text += f"\n{event[eventDescription]}\n\n"

                text += f"\n📆 {datetime.datetime.fromtimestamp(event[6]*1000 / 1e3).strftime('%d %B %Y %H:%M')}\n"

                conditions = {}
                conditions['user_id'] = user_id
                conditions['event_id'] = event[0]
                orders = self.db.fetchone(table='orders', conditions=conditions, closed=False)

                if orders is None:
                    order = True
                else:
                    order = False

                if poll=="admin":

                    text += f"\n\n\nID: {event[0]}"
                    event_btns = eventBtn(event,'admin', False)

                else:

                    event_btns = eventBtn(event,'user', order, user_id=user_id)

                requests.get(f"https://api.telegram.org/bot{token}/sendPhoto?chat_id={chat_id}&photo={event[5]}&reply_markup={event_btns}&caption={text}")

                text = ""

        else:

            text = "Активных событий нет"
            requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}&reply_markup={main}")


    def myEvents(self, chat_id, user_id, token, poll='admin'):

        my_events = self.db.fetchall(
            table='orders',
            columns=['event_id'],
            conditions={'user_id': user_id},
            closed=False
        )

        lang = self.db.fetchone(
            table='users',
            columns=['lang'],
            conditions={'user_id': user_id},
            closed=False
        )

        columns = self.db.getColumns('events')

        text = ''

        lang = self.system.getLang(user_id=user_id)
        eventDescLang = self.system.getEventDescLang(user_id=user_id)

        locale.setlocale(locale.LC_ALL, f"{lang.lower()}_{lang}")
        eventDescription = columns.index(f"event_desc{eventDescLang}")

        if len(my_events)>0:

            for id in my_events:

                current_time = time.time()

                conditions = {}
                conditions['event_id'] = id[0]

                conditions['event_date'] = {}
                conditions['event_date'][0] = int(current_time)
                conditions['event_date'][1] = '>'

                event = self.db.fetchone(table='events', conditions=conditions, closed=False)

                if event is not None:

                    text += f"\n{event[eventDescription]}\n\n"

                    text += f"\n📆 {datetime.datetime.fromtimestamp(event[6]*1000 / 1e3).strftime('%d %B %Y %H:%M')}\n"

                    conditions = {}
                    conditions['user_id'] = user_id
                    conditions['event_id'] = event[0]
                    orders = self.db.fetchone(table='orders', conditions=conditions, closed=False)

                    if orders is None:
                        order = True
                    else:
                        order = False

                    main = eventBtn(alias=event, type="user", ordered=order) # mainBtns(lang=user_id)

                    requests.get(f"https://api.telegram.org/bot{token}/sendPhoto?chat_id={chat_id}&photo={event[5]}&reply_markup={main}&caption={text}")

                    text = ""

        else:

            text = "Активных событий нет"
            requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}")

    def publication(self, event_id):

        self.db.update(
            table='events',
            sets={"sended": 1},
            conditions={'event_id': event_id},
            closed=False
        )

        res = self.db.fetchone(
            table='events',
            columns=['event_id','event_desc','event_date'],
            conditions={"event_id": event_id},
            closed=False
        )

        text = f"\n{res[1]}\n\n"
        text += f"\n📆 {datetime.datetime.fromtimestamp(res[2] * 1000 / 1e3).strftime('%d %B %Y %H:%M')}\n"
        text += f"\n\n\nID: {res[0]}"

        result = [res[0], text]

        return result

    def subscribe(self, event_id, user_id):

        order = self.db.fetchone(
            table='orders',
            conditions={"event_id": event_id,"user_id": user_id},
            closed=False
        )

        if order is None:
            self.db.insert(
                table='orders',
                columns=["event_id","user_id"],
                values=[event_id,user_id],
                closed=False
            )

        lang = self.system.getLang(user_id=user_id)
        eventDescLang = self.system.getEventDescLang(user_id=user_id)

        locale.setlocale(locale.LC_ALL, f"{lang.lower()}_{lang}")

        res = self.db.fetchone(
            table='events',
            columns=['event_id',f'event_desc{eventDescLang}','event_date'],
            conditions={"event_id": event_id},
            closed=False
        )

        text = f"\n{res[1]}\n\n"
        text += f"\n📆 {datetime.datetime.fromtimestamp(res[2] * 1000 / 1e3).strftime('%d %B %Y %H:%M')}\n"

        result = [res[0], text]

        return result