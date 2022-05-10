import psycopg2
import os
from psycopg2 import DatabaseError
from decouple import config

def get_connection():
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        print(DATABASE_URL)
        #DATABASE_URL = 'postgresql://adminDB:3x0w0rks@localhost:5432/DBexoWorks'
        return psycopg2.connect(
        #    host = config('PGSQL_HOST'),
        #   user = config('PGSQL_USER'),
        #  password = config('PGSQL_PASSWORD'),
        #    database = config('PGSQL_DATABASE')
        DATABASE_URL
        
        )
    except DatabaseError as ex:
        raise ex