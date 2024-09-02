import os
port = "5432"
# database = os.environ['DB_NAME']
# username = os.environ['DB_USERNAME']
# password = os.environ['DB_PASSWORD']
# host = os.environ['DB_HOST']
database = "files_db"
password = "Asafba123"
username = "hello"
host = "postgres-db"
connection_string = (
    f"postgres://{username}:{password}@{host}:{port}/{database}")

