import asyncio
import os
import time
import magic
import sqlite3

from sql_queries import get_db_live_files ## TODO ##
queue_count = 0

def return_count():
    return queue_count
def extract_name(filename):
    return os.path.splitext(filename)[0]
def extract_file_type(filename):
    return os.path.splitext(filename)[1]
def is_removed(cursor, filename,file_type):
    cursor.execute('''
                SELECT * FROM files WHERE name=? AND file_type=? AND time_deleted is NOT NULL
                 ''', (filename, file_type))
    exs = cursor.fetchone()
    return exs

# Extracts the data from a single file
def extract_data(path, filename):
    time.sleep(2)
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
    is_text = 0 if 'text' in text else 1 if 'video' in text or 'img' in text or 'image' in text else -1
    return (
        extract_name(filename), time_created, time_modified, time_removed, file_size, file_type, int(is_text))

#tracks the changes in folder
async def track_changes(path):
    global queue_count
    localdb = sqlite3.connect("files.db")
    cursor = localdb.cursor()

    ## TODO ##
    # db_live_files
    # db_deleted_files
    # folder_files

    prev_version = set(f"{row[0]}{row[1]}" for row in cursor.execute('SELECT name,file_type FROM files WHERE time_deleted IS NULL'))
    while True:
        await asyncio.sleep(0.2)

        current_version = set(f"{extract_name(file)}{extract_file_type(file)}" for file in os.listdir(path))
        if current_version != prev_version:
            added = current_version - prev_version
            removed = prev_version - current_version
            prev_version = current_version
            cur_count = 0
            for file in added:
                cur_count = cur_count + 1
                queue_count = len(added) - cur_count
                file_data = extract_data(path, file)
                if file_data is None:
                    continue
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
                    if is_removed(cursor,extract_name(file),extract_file_type(file)):
                        cursor.execute('''
                                UPDATE files
                                SET time_modified=?, time_deleted=?, file_size=?, file_type=?, is_text=?
                                WHERE name=?
                            ''', (*file_data[2:],extract_name(file)))
                localdb.commit()
            for file in removed:
                name = extract_name(str(file))
                cursor.execute('''
                    UPDATE files
                    SET time_deleted = ?
                    WHERE name = ?
                ''', (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),name))
                localdb.commit()
            localdb.commit()

if __name__ == '__main__':
    asyncio.run(track_changes(r"C:\Users\shoam\OneDrive\Desktop\random folder"))
