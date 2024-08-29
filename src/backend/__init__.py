import psycopg2
from settings import connection_string
conn = psycopg2.connect(connection_string)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS files_db (
        name TEXT PRIMARY KEY,
        time_created TEXT,
        time_modified TEXT,
        time_deleted TEXT,
        file_size INTEGER,
        file_type TEXT,
        is_text INTEGER)
    ''')
conn.commit()