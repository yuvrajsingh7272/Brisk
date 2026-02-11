import psycopg2
import os

from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')
DB_URL = os.getenv("DATABASE_URL")

conn = None
try:
    conn = psycopg2.connect(DB_URL)
    print("DATABASE CONNECTION SUCESSFULL")

    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS chat_history (id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), prompt TEXT, answer TEXT)")

    conn.commit()
    cur.close()
    print("TABLES CREATED SUCESSFULLY")

except (Exception, psycopg2.DatabaseError) as error:
    print(f"Error: {error}")

finally:
    if conn is not None:
        conn.close()

