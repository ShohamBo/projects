import os
import time
import pandas as pd
import sqlite3
import dash
from dash import dcc, html
import plotly.express as px
import magic
import pathlib


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
        filename.removesuffix(file_type), time_created, time_modified, time_removed, file_size, file_type, int(is_text))


def track_changes(path):
    localdb = sqlite3.connect("files.db")
    cursor = localdb.cursor()
    prev_version = set()

    while True:
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
        time.sleep(10)

if __name__ == '__main__':
    track_changes(r"C:\Users\shoam\OneDrive\Desktop\random folder")