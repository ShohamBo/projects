import pyodbc

server = 'localhost,1433'
database = 'files'
username = 'hello'
password = 'asafba'
driver = '{ODBC Driver 17 for SQL Server}'
connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()
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

