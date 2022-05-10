import psycopg2
import os
from psycopg2 import DatabaseError
from decouple import config

def get_connection():
    try:
        #DATABASE_URL = os.environ.get('DATABASE_URL')
        DATABASE_URL = 'postgres://kbeqwsfgqwkxui:5f7c44f61a7f07badb4c9744daa1f5c5c3763b1eaf83dd5a277c5547bec1899e@ec2-3-231-82-226.compute-1.amazonaws.com:5432/dfdt60gdue5iln'
        
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