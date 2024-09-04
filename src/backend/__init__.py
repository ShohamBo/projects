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
        is_text INTEGER,
        count_files_waiting INTEGER)
        
    ''')
conn.commit()
cursor.execute('''
    SELECT * FROM files_db WHERE name = %s
''', ('-111',))
if cursor.fetchone() is None:
    cursor.execute('''
            INSERT INTO files_db (name, time_created, time_modified, time_deleted, file_size, file_type, is_text, count_files_waiting)
            VALUES ('-111', NULL, NULL, '-1', NULL, NULL, NULL, 0)
        ''')
conn.commit()