import os
import mysql.connector
from dotenv import load_dotenv

# Load the secret credentials from the .env file
load_dotenv()

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None