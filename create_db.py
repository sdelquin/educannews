import sqlite3
import config
import os
import sys
import crayons

db = config.DATABASE

if os.path.isfile(db):
    print(
        crayons.red(
            f'''Database {db} already exists.
If you continue it will be DESTROYED!! Continue? [y/N] ''',
            bold=True
        ),
        end=''
    )
    option = input()
    if option.upper() == 'Y':
        os.remove(db)
        print('{} {} {}'.format(
            'Database',
            crayons.white(db, bold=True),
            crayons.green('successfully deleted!')
        ))
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

print('{} {} {}'.format(
    'Database',
    crayons.white(db, bold=True),
    crayons.green('successfully created!')
))

print('{} {} {}'.format(
    'Table',
    crayons.white('news', bold=True),
    crayons.green('successfully created!')
))
