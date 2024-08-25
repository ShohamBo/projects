import sqlite3
localdb = sqlite3.connect('dbs/files.db')
cursor = localdb.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        name TEXT PRIMARY KEY,
        time_created TEXT,
        time_modified TEXT,
        time_deleted TEXT,
        file_size INTEGER,
        file_type TEXT,
        is_text BOOLEAN NOT NULL)
    ''')
localdb.commit()
localdb.close()
