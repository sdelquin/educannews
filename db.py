import sqlite3
import os
import sys

import crayons

import config


def create_db():
    db_path = config.DATABASE
    if os.path.isfile(db_path):
        print(
            crayons.red(
                f'''Database {db_path} already exists.
    If you continue it will be DESTROYED!! Continue? [y/N] ''',
                bold=True
            ),
            end=''
        )
        option = input()
        if option.upper() == 'Y':
            os.remove(db_path)
            print('{} {} {}'.format(
                'Database',
                crayons.white(db_path, bold=True),
                crayons.green('successfully deleted!')
            ))
        else:
            sys.exit()

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # table of news
    c.execute(
        '''
        CREATE TABLE news
        (title text,
        date text,
        url text,
        category text,
        saved_at datetime,
        tg_msg_id int unique)
        '''
    )
    conn.commit()
    conn.close()

    print('{} {} {}'.format(
        'Database',
        crayons.white(db_path, bold=True),
        crayons.green('successfully created!')
    ))

    print('{} {} {}'.format(
        'Table',
        crayons.white('news', bold=True),
        crayons.green('successfully created!')
    ))


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def init_db():
    dbconn = sqlite3.connect(config.DATABASE)
    dbconn.row_factory = dict_factory
    dbcur = dbconn.cursor()
    return dbconn, dbcur
