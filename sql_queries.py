import sqlite3
import time

import pandas as pd

from src.folder_functions import extract_data

is_text_translator = {0: 'text', 1: 'video', -1: 'no clue'}
localdb = sqlite3.connect(r'dbs/files.db')
global cursor
cursor = localdb.cursor()


# def create_connection():
#
#     localdb = sqlite3.connect('files.db')
#     cursor = localdb.cursor()
#     return cursor


def commit_db():
    localdb.commit()


def get_db_live_files():
    global cursor
    return set(
        f"{row[0]}{row[1]}" for row in cursor.execute('SELECT name,file_type FROM files WHERE time_deleted IS NULL'))


def get_db_deleted_files():
    global cursor
    return set(f"{row[0]}{row[1]}" for row in
               cursor.execute('SELECT name,file_type FROM files WHERE time_deleted IS NOT NULL'))


def add_file_to_db(db_file):
    global cursor
    cursor.execute('''
            INSERT INTO files (name, time_created, time_modified, time_deleted, file_size, file_type, is_text)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', extract_data(db_file))
    commit_db()


def remove_file_from_db(filename):
    global cursor
    cursor.execute('''
            UPDATE files
            SET time_deleted = ?
            WHERE name = ?
        ''', (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), filename,))
    commit_db()


def is_file_in_db(filename):
    global cursor
    cursor.execute('''
                        SELECT * FROM files WHERE name=?
                    ''', (filename,))
    return bool(cursor.fetchone())


def change_returning_files(filename):
    cursor.execute('''
                    UPDATE files
                    SET time_deleted=NULL
                    WHERE name=?
                ''', (filename,))
    commit_db()


def fetch_data():
    localdb = sqlite3.connect('dbs/files.db')
    cursor = localdb.cursor()
    df = pd.read_sql_query('SELECT * FROM files WHERE time_deleted IS NULL', localdb)
    df['is_text'] = df['is_text'].map(is_text_translator)
    return df


def df_full_by_binary_count(is_text):
    localdb = sqlite3.connect('dbs/files.db')
    if is_text or is_text == 0:
        df_modified = pd.read_sql_query(
            'SELECT * FROM files WHERE time_deleted IS NULL AND is_text = ?', localdb,
            params=(is_text,))
        df_modified['is_text'] = df_modified['is_text'].map(
            is_text_translator)  # change the description on the right
        return df_modified
    else:
        df_modified = pd.read_sql_query('SELECT * FROM files WHERE time_deleted IS NULL', localdb)
        df_modified['is_text'] = df_modified['is_text'].map(
            is_text_translator)  # change the description on the right
        return df_modified


def df_count_by_binary_type(is_text):
    localdb = sqlite3.connect('dbs/files.db')
    if is_text or is_text == 0:
        df_modified = pd.read_sql_query(
            'SELECT file_size, COUNT(*) as count FROM files WHERE time_deleted IS NULL AND is_text = ? GROUP BY file_size',
            localdb,
            params=(is_text,))
        return df_modified
    else:
        df = pd.read_sql_query(
            'SELECT file_size, COUNT(*) as count FROM files WHERE time_deleted IS NULL GROUP BY file_size', localdb)
        return df


