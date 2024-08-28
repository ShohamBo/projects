import os
port = "5432"
database = os.environ['DB_NAME']
username = os.environ['DB_USERNAME']
password = os.environ['DB_PASSWORD']
host = "postgres_db"

connection_string = (
    f"postgres://{username}:{password}@{host}:{port}/{database}")

