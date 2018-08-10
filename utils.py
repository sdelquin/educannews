import sqlite3
import datetime
import config
import re


def add_chat(chat):
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%f')
    if chat.title:
        long_name = chat.title
    else:
        long_name = f'{chat.first_name} {chat.last_name}'
    try:
        cur.execute(f'''insert into chat values (
            '{chat.id}', '{long_name}', '{now}'
        )''')
    except sqlite3.IntegrityError:
        return False
    conn.commit()
    return True


def delete_chat(chat):
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    result = cur.execute(f"delete from chat where telegram_id = '{chat.id}'")
    conn.commit()
    return result.rowcount > 0


def hash_category(category):
    return '#' + re.sub(r',\s*|\s+', '', category.title())
