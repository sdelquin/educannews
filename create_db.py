import sqlite3
import config

conn = sqlite3.connect(config.DATABASE)
c = conn.cursor()
c.execute(
    '''
    CREATE TABLE news
    (title text, date text, url text, category text, saved_at datetime)
    '''
)
conn.commit()
conn.close()
