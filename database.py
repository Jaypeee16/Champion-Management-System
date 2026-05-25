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

def log_action(user_id, action_type, module, details):
    """
    Universal logger — logs ALL system activity.
    Auto-prunes to keep only the latest 10,000 records (storage safety net for 1 GB DB).
    Call this from any module: log_action(user_id, "Viewed", "Inventory", "Opened inventory list")
    """
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # 1. Insert the new log
            cursor.execute(
                "INSERT INTO system_logs (user_id, action_type, module, details) VALUES (%s, %s, %s, %s)",
                (user_id, action_type, module, details)
            )
            # 2. Storage Safety Net: Keep only the latest 10,000 records to prevent DB bloat
            #    At ~500 bytes per log, 10,000 logs ≈ 5 MB — negligible on a 1 GB DB.
            cursor.execute("""
                DELETE FROM system_logs
                WHERE log_id NOT IN (
                    SELECT log_id FROM (
                        SELECT log_id FROM system_logs ORDER BY timestamp DESC LIMIT 10000
                    ) foo
                )
            """)
            conn.commit()
        except Exception as e:
            print(f"Log Error: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()