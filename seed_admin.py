import bcrypt
from database import get_connection

def seed_admin():
    print("Connecting to the database...")
    conn = get_connection()
    if not conn:
        print("❌ Failed to connect to the database.")
        return

    try:
        cursor = conn.cursor()
        
        # Default Admin Credentials
        emp_id = "admin"
        name = "System Admin"
        raw_password = "password123"
        role = "Admin"

        print("Generating secure password hash...")
        hashed_pw = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Check if the admin account already exists
        cursor.execute("SELECT * FROM user WHERE employee_id = %s", (emp_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"⚠️ Account '{emp_id}' found! Forcing password reset...")
            # FORCE UPDATE THE PASSWORD
            cursor.execute("UPDATE user SET password_hash = %s WHERE employee_id = %s", (hashed_pw, emp_id))
            print("✅ Password successfully overridden!")
        else:
            print(f"Injecting new '{emp_id}' account...")
            # INSERT NEW ACCOUNT
            cursor.execute("""
                INSERT INTO user (employee_id, full_name, password_hash, role)
                VALUES (%s, %s, %s, %s)
            """, (emp_id, name, hashed_pw, role))
            print("✅ Account injected successfully!")

        conn.commit()
        print("-" * 30)
        print(f"Employee ID (Username): {emp_id}")
        print(f"Password:               {raw_password}")
        print("-" * 30)
        print("You can now log in to the system!")

    except Exception as e:
        print(f"\n❌ Database Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    seed_admin()