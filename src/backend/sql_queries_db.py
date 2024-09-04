import time
import pandas as pd
import psycopg2
from settings import connection_string
from folder_functions import extract_data
is_text_translator = {0: 'text', 1: 'video', -1: 'no clue'}
db = psycopg2.connect(connection_string)
global cursor
cursor = db.cursor()


def commit_db():
    db.commit()


def new_connection(connection_string):
    db = psycopg2.connect(connection_string)
    return db


def get_db_live_files():
    global cursor
    cursor.execute('SELECT name,file_type FROM files_db WHERE time_deleted IS NULL')
    rows = cursor.fetchall()
    return set(f"{row[0]}{row[1]}" for row in rows)


def get_db_deleted_files():
    global cursor
    cursor.execute('SELECT name,file_type FROM files_db WHERE time_deleted IS NOT NULL')
    rows = cursor.fetchall()
    return set(f"{row[0]}{row[1]}" for row in rows)



def add_file_to_db(path, db_file):
    global cursor
    cursor.execute('''
            INSERT INTO files_db (name, time_created, time_modified, time_deleted, file_size, file_type, is_text,count_files_waiting)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', extract_data(path, db_file))
    commit_db()


def remove_file_from_db(filename):
    global cursor
    cursor.execute('''
            UPDATE files_db
            SET time_deleted = %s
            WHERE name = %s
        ''', (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), filename,))
    commit_db()


def is_file_in_db(filename):
    global cursor
    cursor.execute('''
                        SELECT * FROM files_db WHERE name= %s
                    ''', (filename,))
    return cursor.fetchone()


def change_returning_files(filename):
    global cursor
    cursor.execute('''
            UPDATE files_db
            SET time_deleted=NULL
            WHERE name=%s
        ''', (filename,))
    commit_db()

def insert_files_waiting(count):
    global cursor
    print("inserted", count)
    cursor.execute('''
    UPDATE files_db
    SET count_files_waiting = %s
    WHERE name=%s
    ''', (count, '-111'))




