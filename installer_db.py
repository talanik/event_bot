import sqlite3

conn = sqlite3.connect("maindb.db")
cursor = conn.cursor()

# cursor.execute("DROP TABLE users")
cursor.execute("""CREATE TABLE if not exists localize (
                                                        alias text, 
                                                        ru text, 
                                                        uz text
                                                     )""")

cursor.execute("""CREATE TABLE if not exists users (
                                                        user_id int, 
                                                        user_name text, 
                                                        phone text,
                                                        edu text,
                                                        chat_id int,
                                                        lang text
                                                     )""")

cursor.execute("""CREATE TABLE if not exists temp_users (
                                                        user_id int, 
                                                        user_name text, 
                                                        phone text,
                                                        edu text,
                                                        chat_id int,
                                                        lang text
                                                     )""")

cursor.execute("""CREATE TABLE if not exists events (
                                                        event_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                                                        event_name text, 
                                                        event_name_uz text, 
                                                        event_desc text, 
                                                        event_desc_uz text, 
                                                        image text, 
                                                        event_date int,
                                                        event_limit int,
                                                        sended int
                                                    )""")

cursor.execute("""CREATE TABLE if not exists orders (
                                                        user_id int, 
                                                        event_id int
                                                    )""")

cursor.execute("""CREATE TABLE if not exists agents (
                                                        agent_id int, 
                                                        department text, 
                                                        fio text
                                                    )""")

conn.commit()

conn.close()
