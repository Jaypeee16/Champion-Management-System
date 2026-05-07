import bcrypt
from database import get_connection

def create_first_admin():
    conn = get_connection()
    if not conn:
        print("Could not connect to database.")
        return

    cursor = conn.cursor()
    
    # 1. Create the password bytes
    password = b"admin123"
    
    # 2. Generate the salt and hash (these remain as raw bytes)
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(password, salt)
    
    # 3. Decode ONLY right before inserting into the VARCHAR column
    hashed_password_string = hashed_password_bytes.decode('utf-8')

    sql = """
    INSERT INTO User (employee_id, full_name, email, role, password_hash)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = ('admin', 'System Administrator', 'admin@champion.com', 'Admin', hashed_password_string)
    
    try:
        cursor.execute(sql, values)
        conn.commit()
        print("Success! Admin created.")
        print("Username: admin | Password: admin123")
        
        # Verify exactly what was saved to the database
        cursor.execute("SELECT password_hash FROM User WHERE employee_id = 'admin'")
        saved_hash = cursor.fetchone()[0]
        print(f"DEBUG - Hash saved to DB: {saved_hash}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_first_admin()