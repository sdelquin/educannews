import os
import sqlite3
import sys

import crayons

import settings


def create_db(db_path=settings.DATABASE, force_delete=False, verbose=True):
    if os.path.isfile(db_path):
        if not force_delete:
            print(
                crayons.red(
                    f"""Database {db_path} already exists.
        If you continue it will be DESTROYED!! Continue? [y/N] """,
                    bold=True,
                ),
                end='',
            )
        if force_delete:
            option = 'y'
            if verbose:
                print(crayons.cyan(f'{os.linesep}Force delete enabled'))
        else:
            option = input()
        if option.upper() == 'Y':
            os.remove(db_path)
            if verbose:
                print(
                    '{} {} {}'.format(
                        'Database',
                        crayons.white(db_path, bold=True),
                        crayons.green('successfully deleted!'),
                    )
                )
        else:
            sys.exit()

    conn, cur = init_db(db_path)
    # table of news
    cur.execute(
        """
        CREATE TABLE news
        (title text,
        date text,
        topics text,
        url text,
        summary text,
        saved_at datetime,
        tg_msg_id int unique)
        """
    )
    conn.commit()

    if verbose:
        print(
            '{} {} {}'.format(
                'Database',
                crayons.white(db_path, bold=True),
                crayons.green('successfully created!'),
            )
        )
        print(
            '{} {} {}'.format(
                'Table',
                crayons.white('news', bold=True),
                crayons.green('successfully created!'),
            )
        )

    return conn, cur


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def init_db(db_path=settings.DATABASE):
    dbconn = sqlite3.connect(db_path)
    dbconn.row_factory = dict_factory
    dbcur = dbconn.cursor()
    return dbconn, dbcur
