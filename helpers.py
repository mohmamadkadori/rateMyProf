import os, psycopg2


def get_db():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable is not set!")
    
    conn = psycopg2.connect(DATABASE_URL)
    return conn