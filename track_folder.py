import asyncio
import os
import sqlite3
import time
import magic
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import zipfile


def extract_name(filename):
    return (os.path.splitext(filename)[0])


def extract_file_type(filename):
    return os.path.splitext(filename)[1]


def is_removed(cursor, filename, file_type):
    cursor.execute('''
                SELECT * FROM files WHERE name=? AND file_type=? AND time_deleted is not NULL
                 ''', (filename, file_type))
    exs = cursor.fetchone()
    return exs


# Extracts the data from a single file
def extract_data(path, filename):
    full_path = os.path.join(path, filename)
    if not os.path.isfile(full_path):
        return None
    time_created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(full_path)))
    time_modified = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(full_path)))
    time_removed = None
    file_size = os.path.getsize(full_path)
    file_type = os.path.splitext(full_path)[1]
    mime_type = magic.Magic(mime=True)
    text = mime_type.from_file(full_path)
    is_text = 0 if 'text' in text else 1 if 'video' in text else -1
    return (
        os.path.splitext(filename)[0], time_created, time_modified, time_removed, file_size, file_type, int(is_text))


def add_file_to_db(localdb, path):
    localdb = sqlite3.connect("files.db")
    cursor = localdb.cursor()

    for file in os.listdir(path):
        file_data = extract_data(path, file)
        if file_data is None:
            None
        cursor.execute('''
                    SELECT * FROM files WHERE name=?
                ''', (extract_name(file),))
        exs = cursor.fetchone()
        if not exs:
            cursor.execute('''
                INSERT INTO files (name, time_created, time_modified, time_deleted, file_size, file_type, is_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', file_data)
        else:
            if is_removed(cursor, extract_name(file), extract_file_type(file)):
                cursor.execute('''
                    UPDATE files
                    SET time_modified=?, time_deleted=?, file_size=?, file_type=?, is_text=?
                    WHERE name=?
                        ''', (*file_data[2:], (extract_name(file))))
        localdb.commit()


def remove_file_from_db(filename, path):

    localdb = sqlite3.connect("files.db")
    cursor = localdb.cursor()
    for file in os.listdir(path):
        cursor.execute('''
            UPDATE files
            SET time_deleted = ?
            WHERE name = ?
                ''', (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), extract_name(file)))
        localdb.commit()

class WatchdogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        super().on_modified(event)
        if event.is_directory:
            add_file_to_db(event.src_path)
# tracks the changes in folder
async def track_changes(path):
    localdb = sqlite3.connect("files.db")
    cursor = localdb.cursor()
    prev_version = set()

    while True:
        await asyncio.sleep(5)



if __name__ == '__main__':
    asyncio.run(track_changes(r"C:\Users\shoam\OneDrive\Desktop\random folder"))
