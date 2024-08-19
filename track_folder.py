import os
import time
import pandas as pd
import sqlite3
import dash
from dash import dcc, html
import plotly.express as px
import magic


def print_localdb(localdb):
    cursor = localdb.cursor()
    cursor.execute('SELECT * FROM files')
    rows = cursor.fetchall()
    return [html.Pre(str(row)) for row in rows]


def extract_name(filename):
    return filename.rstrip(os.path.splitext(filename)[1])


# Extracts the data from a single file
def extract_data(path, filename):
    text_extensions = {'.txt', '.csv', '.html', '.xml'}
    full_path = os.path.join(path, filename)
    time_created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(full_path)))
    time_modified = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(full_path)))
    time_removed = None
    file_size = os.path.getsize(full_path)
    file_type = os.path.splitext(full_path)[1]
    mime_type = magic.Magic(mime=True)
    text = mime_type.from_file(full_path)
    is_text = 0 if 'text' in text else 1 if 'video' in text else -1
    return (
        filename.rstrip(file_type), time_created, time_modified, time_removed, file_size, file_type, int(is_text))


# Handles tracking changes and updating the database
def track_changes(path):

    localdb = sqlite3.connect("files.db")
    cursor = localdb.cursor()
    prev_version = set()

    while True:
        time.sleep(10)
        current_version = set(os.listdir(path))
        if current_version != prev_version:
            added = current_version - prev_version
            removed = prev_version - current_version
            prev_version = current_version
            for file in added:
                cursor.execute('''
                    SELECT * FROM files WHERE name=?
                ''', (extract_name(file),))
                exs = cursor.fetchone()
                if not exs:
                    cursor.execute('''
                        INSERT INTO files (name, time_created, time_modified, time_deleted, file_size, file_type, is_text)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', extract_data(path, file))
            for file in removed:
                cursor.execute('''
                    UPDATE files
                    SET time_deleted = ?
                    WHERE name = ?
                ''', (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), extract_name(file)))
            localdb.commit()
            dashboard(localdb)


def dashboard(localdb):
    app = dash.Dash(__name__)
    localdb = sqlite3.connect("files.db")
    df = pd.read_sql_query('SELECT * FROM files WHERE time_deleted is NULL', localdb)
    app.layout = html.Div([
        dcc.Graph(
            id='file_size_bar',
            figure=px.bar(df, x='name', y='file_size', title='File Size bar')
        ),
        dcc.Graph(
            id='percent-binary',
            figure=px.pie(df, names='is_text', title='text vs binary files')
        ),
        dcc.Graph(
            id='file_type_pie',
            figure=px.pie(df, names='file_type', title='file types')
        )
    ])
    app.run_server(debug=True)
    localdb.close()

    if __name__ == '__main__':
        app.run_server(debug=True)


def main():
    localdb = sqlite3.connect("files.db")
    cursor = localdb.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            name TEXT PRIMARY KEY,
            time_created TEXT,
            time_modified TEXT,
            time_deleted TEXT,
            file_size INTEGER,
            file_type TEXT,
            is_text BOOLEAN NOT NULL
        )
    ''')
    localdb.commit()
    localdb.close()
    path = r"C:\Users\shoam\OneDrive\Desktop\random folder"

    track_changes(path)
    dashboard(localdb)


if __name__ == "__main__":
    main()
