import os, psycopg2


DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:[YOUR-PASSWORD]@db.gnqtismdbgwyyzcxgneg.supabase.co:5432/postgres')

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn