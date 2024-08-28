import asyncio
import logging
import os
from database.sql_queries_db import *
from tracker.folder_functions import *
queue_count = 0


def fqueue_count():
    return queue_count


log_file_path = '/app/log/app.log'
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)  # Ensure the logs directory exists

logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info("this is not a banger")


# tracks the changes in folder
async def track_changes(path):
    logging.info(f'Tracking {path}')
    global queue_count
    while True:
        await asyncio.sleep(0.2)
        db_live_files = get_db_live_files()
        folder_files = set(os.listdir(path))
        db_deleted_files = get_db_deleted_files()
        if folder_files != db_live_files:
            added = folder_files - db_live_files
            removed = db_live_files - folder_files
            cur_count = 0
            for file in added:
                logging.info(f'Adding {file}')
                cur_count = cur_count + 1
                queue_count = len(added) - cur_count
                if extract_data(path, file) is None:
                    continue
                if not is_file_in_db(extract_name(file)) and file not in db_deleted_files:
                    add_file_to_db(path, file)
                elif file in db_deleted_files:
                    change_returning_files(extract_name(file))
                elif is_file_in_db(extract_name(file)):
                    pass
            for file in removed:
                remove_file_from_db(extract_name(file))
