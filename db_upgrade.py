from database import get_connection

def upgrade_database():
    print("Connecting to Aiven to upgrade database schema...")
    try:
        conn = get_connection()
        if not conn:
            print("❌ ABORTED: Could not reach the database. Check your network or Aiven IP Filter.")
            return
            
        cursor = conn.cursor()
        
        # Add the missing columns to the 'tool' table
        cursor.execute("ALTER TABLE tool ADD COLUMN category VARCHAR(100) DEFAULT 'Tools'")
        cursor.execute("ALTER TABLE tool ADD COLUMN price DECIMAL(10,2) DEFAULT 0.00")
        cursor.execute("ALTER TABLE tool ADD COLUMN location VARCHAR(100) DEFAULT 'N/A'")
        
        conn.commit()
        print("✅ SUCCESS: Database upgraded! Category, Price, and Location added.")
    except Exception as e:
        # If it says 'Duplicate column name', it just means you already ran it!
        print(f"Result: {e}")
    finally:
        # Fixed the NoneType bug here!
        if 'conn' in locals() and conn is not None and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    upgrade_database()