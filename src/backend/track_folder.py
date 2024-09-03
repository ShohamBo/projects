import __init__
import asyncio
from folder_functions import *
from sql_queries_db import *
queue_count = 0


# def fqueue_count():
#     return queue_count


# tracks the changes in folder
async def track_changes(path):
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
                cur_count = cur_count + 1
                queue_count = len(added) - cur_count
                if extract_data(path, file) is None:
                    continue
                if not is_file_in_db(extract_name(file)) and file not in db_deleted_files:
                    print(f'{file} is about to be added')
                    add_file_to_db(path, file)
                elif file in db_deleted_files:
                    change_returning_files(extract_name(file))
                elif is_file_in_db(extract_name(file)):
                    pass
            for file in removed:
                remove_file_from_db(extract_name(file))

if __name__ == '__main__':
    asyncio.run(track_changes("/update-db/local-data"))