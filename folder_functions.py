import logging
import os
import time
import magic


def extract_name(filename):
    return os.path.splitext(filename)[0]


def extract_file_type(filename):
    return os.path.splitext(filename)[1]


# Extracts the data from a single file
def extract_data(path, filename):
    # time.sleep(2)
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
