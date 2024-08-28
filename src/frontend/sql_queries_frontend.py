import pandas as pd
import psycopg2
from settings import connection_string
is_text_translator = {0: 'text', 1: 'video', -1: 'no clue'}
db = psycopg2.connect(connection_string)
global cursor
cursor = db.cursor()


def commit_db():
    db.commit()


def new_connection(connection_string):
    db = psycopg2.connect(connection_string)
    return db


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
