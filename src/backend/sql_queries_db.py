import time
import pandas as pd
import psycopg2
from settings import connection_string
from folder_functions import extract_data
is_text_translator = {0: 'text', 1: 'video', -1: 'no clue'}
db = psycopg2.connect(connection_string)
global cursor
cursor = db.cursor()
cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='files_db');")
print(cursor.fetchone()[0])

def commit_db():
    db.commit()


def new_connection(connection_string):
    db = psycopg2.connect(connection_string)
    return db


def get_db_live_files():
    global cursor
    return set(
        f"{row[0]}{row[1]}" for row in cursor.execute('SELECT name,file_type FROM files_db WHERE time_deleted IS NULL'))


def get_db_deleted_files():
    global cursor
    print(cursor.description)
    return set(f"{row[0]}{row[1]}" for row in
               cursor.execute('SELECT name,file_type FROM files_db WHERE time_deleted IS NOT NULL'))


def add_file_to_db(path, db_file):
    global cursor
    cursor.execute('''
            INSERT INTO db (name, time_created, time_modified, time_deleted, file_size, file_type, is_text)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', extract_data(path, db_file))
    commit_db()


def remove_file_from_db(filename):
    global cursor
    cursor.execute('''
            UPDATE files_db
            SET time_deleted = ?
            WHERE name = ?
        ''', (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), filename,))
    commit_db()


def is_file_in_db(filename):
    global cursor
    cursor.execute('''
                        SELECT * FROM db WHERE name=?
                    ''', (filename,))
    return bool(cursor.fetchone())


def change_returning_files(filename):
    cursor.execute('''
                    UPDATE files_db
                    SET time_deleted=NULL
                    WHERE name=?
                ''', (filename,))
    commit_db()


def fetch_data():
    db = new_connection(connection_string)
    df = pd.read_sql_query('SELECT * FROM files_db WHERE time_deleted IS NULL', db)
    df['is_text'] = df['is_text'].map(is_text_translator)
    return df


def df_full_by_binary_count(is_text):
    db = new_connection(connection_string)
    if is_text or is_text == 0:
        df_modified = pd.read_sql_query(
            'SELECT * FROM files_db WHERE time_deleted IS NULL AND is_text = ?', db,
            params=(is_text,))
        df_modified['is_text'] = df_modified['is_text'].map(
            is_text_translator)  # change the description on the right
        return df_modified
    else:
        df_modified = pd.read_sql_query('SELECT * FROM files_db WHERE time_deleted IS NULL', db)
        df_modified['is_text'] = df_modified['is_text'].map(
            is_text_translator)  # change the description on the right
        return df_modified


def df_count_by_binary_type(is_text):
    db = new_connection(connection_string)
    if is_text or is_text == 0:
        df_modified = pd.read_sql_query(
            'SELECT file_size, COUNT(*) as count FROM files_db WHERE time_deleted IS NULL AND is_text = ? GROUP BY file_size',
            db,
            params=(is_text,))
        return df_modified
    else:
        df = pd.read_sql_query(
            'SELECT file_size, COUNT(*) as count FROM files_db WHERE time_deleted IS NULL GROUP BY file_size', db)
        return df
