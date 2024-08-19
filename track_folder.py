import os
import time
import pandas as pd
import sqlite3
import dash
from dash import dcc, html
import plotly.express as px
import threading
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
    if 'text' in text:
        is_text = 0
    elif 'video' in text:
        is_text = 1
    else:
        is_text = -1

    return (
        filename.rstrip(file_type), time_created, time_modified, time_removed, file_size, file_type, int(is_text),
        False)


# Handles tracking changes and updating the database
def track_changes(path):
    localdb = sqlite3.connect("files.db")
    cursor = localdb.cursor()
    prev_version = set(os.listdir(path))

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


def dashboard(localdb):
    app = dash.Dash(__name__)

    def get_data():
        localdb = sqlite3.connect("files.db")
        df = pd.read_sql_query('SELECT * FROM files WHERE time_deleted is not NULL', localdb)
        localdb.close()
        return df

    app.layout = html.Div([
        dcc.Interval(
            id='interval-component',
            interval=10 * 1000,
            n_intervals=0
        ),
        dcc.Graph(id='file_size_bar'),
        dcc.Graph(id='percent_binary'),
        dcc.Graph(id='file_type_pie')
    ])

    @app.callback(
        [dash.dependencies.Output('file_size_bar', 'figure'),
         dash.dependencies.Output('percent_binary', 'figure'),
         dash.dependencies.Output('file_type_pie', 'figure')],
        [dash.dependencies.Input('interval-component', 'n_intervals')]
    )
    def update_graphs():
        df = get_data()
        fig1 = px.bar(df, x='name', y='file_size', title='File Size Bar')
        fig2 = px.pie(df, names='is_text', title='Text vs Binary Files')
        fig3 = px.pie(df, names='file_type', title='File Types')
        return fig1, fig2, fig3

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

    # Run track_changes separately so they can both run forever
    track_thread = threading.Thread(target=lambda: track_changes(path))
    track_thread.daemon = True
    track_thread.start()
    dashboard(localdb)


if __name__ == "__main__":
    main()
