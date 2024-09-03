import os
# print(os.environ)
database = os.environ['POSTGRES_DB']
username = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
port = "5432"
# database = "files_db"
# password = "Asafba123"
# username = "hello"
host = "postgresdb"
connection_string = (
    f"postgres://{username}:{password}@{host}:{port}/{database}")
print(connection_string)











