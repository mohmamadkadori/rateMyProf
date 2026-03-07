import os
from flask import Flask
import psycopg2

app = Flask(__name__)

@app.route('/')
def index():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    html = "<h1>Debug Info</h1>"
    
    # Check 1: Environment variable
    if not DATABASE_URL:
        html += "<p>❌ DATABASE_URL not set</p>"
        return html
    
    html += "<p>✅ DATABASE_URL is set</p>"
    html += f"<p>URL starts with: {DATABASE_URL[:30]}...</p>"
    
    # Check 2: Try to connect
    try:
        html += "<p>Attempting connection...</p>"
        conn = psycopg2.connect(DATABASE_URL)
        html += "<p>✅ Connection successful!</p>"
        
        # Check 3: Try a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        html += f"<p>✅ PostgreSQL version: {version[:50]}...</p>"
        
        cursor.close()
        conn.close()
        html += "<p>✅ Everything works!</p>"
        
    except psycopg2.OperationalError as e:
        html += f"<p>❌ Connection failed: {str(e)[:200]}</p>"
    except Exception as e:
        html += f"<p>❌ Unexpected error: {str(e)[:200]}</p>"
    
    return html