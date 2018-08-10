import sqlite3
import config
import os
import sys

db = config.DATABASE

if os.path.isfile(db):
    print(f'''Database {db} already exists.
If you continue it will be DESTROYED!! Continue? [y/N] ''', end='')
    option = input()
    if option.upper() == 'Y':
        os.remove(db)
    else:
        sys.exit()

conn = sqlite3.connect(db)
c = conn.cursor()
# table of news
c.execute(
    '''
    CREATE TABLE news
    (title text, date text, url text, category text, saved_at datetime)
    '''
)
conn.commit()
conn.close()
