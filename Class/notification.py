import datetime
import locale

from datetime import datetime

import requests

from Class.db import DB
from Class.system import SYSTEM
from keyboards import eventBtn, mainBtns


class NOTIFICATION():
    """Work with system commands"""

    def __init__(self):
        """Initsialition"""
        self.db = DB()
        self.system = SYSTEM()
        self.token = self.system.getToken()


    def newEvent(self, event):

        users = self.db.fetchall(
            table='users',
            columns=['chat_id', 'lang', 'user_id'],
            closed=False
        )

        event = self.db.fetchone(
            table='events',
            conditions={"event_id": event},
            closed=False
        )

        for ids in users:
            columns = self.db.getColumns('events')

            eventDescLang = self.system.getEventDescLang(user_id=ids[2])

            # locale.setlocale(locale.LC_ALL, f"{ids[1].lower()}_{ids[1]}")
            eventDescription = columns.index(f"event_desc{eventDescLang}")
            picture = columns.index(f"image")

            text = ''
            text += f"\n{event[eventDescription]}\n\n"
            text += f"\n📆 {datetime.fromtimestamp(event[6] * 1000 / 1e3).strftime('%d %B %Y %H:%M')}\n"

            event_btns = eventBtn(event, 'user', True)

            requests.get(
                f"https://api.telegram.org/bot{self.token}/sendPhoto?chat_id={ids[0]}&reply_markup={event_btns}&photo={event[picture]}&caption={text}")


    def remind(self):

        date = datetime.now()
        hour = date.time().hour

        max = hour+(23-hour)*3600

        conditions = {}

        conditions['event_date'] = {}

        conditions['event_date'][0] = int(date.timestamp())
        conditions['event_date'][1] = '>'

        events = self.db.fetchall(
            table='events',
            columns=['event_id', 'event_date'],
            conditions=conditions,
            closed=False
        )

        for ev in events:

            date = datetime.fromtimestamp(int(ev[1]))

            if hour < date.hour < max:

                users = self.db.fetchall(
                    table='orders',
                    columns=['user_id'],
                    conditions={'event_id': ev[0]},
                    closed=False
                )


                for user in users:

                    chat_id = self.db.fetchone(
                        table='users',
                        columns=['chat_id'],
                        conditions={"user_id": user[0]},
                        closed=False
                    )

                    lang = self.system.getLang(user_id=user[0])
                    eventDescLang = self.system.getEventDescLang(user_id=user[0])

                    # locale.setlocale(locale.LC_ALL, f"{lang.lower()}_{lang}")


                    event = self.db.fetchone(
                        table='events',
                        columns=[f"event_name{eventDescLang}", f"event_desc{eventDescLang}","image"],
                        conditions={"event_id": ev[0]},
                        closed=False
                    )

                    text = self.system.getlocalize(user_id=user[0], alias="notify_text")
                    text = text.replace("{event_name}",event[0]).replace("{event_date}", date.strftime('%d %B %Y %H:%M:%S'), )

                    main = mainBtns(lang=user[0])

                    requests.get(f"https://api.telegram.org/bot{self.token}/sendPhoto?chat_id={chat_id[0]}&photo={event[2]}&reply_markup={main}&caption={text}")