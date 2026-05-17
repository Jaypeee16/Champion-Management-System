from database import get_connection

def upgrade_database():
    print("Connecting to Aiven to upgrade database schema...")
    try:
        conn = get_connection()
        if not conn:
            print("❌ ABORTED: Could not reach the database. Check your network or Aiven IP Filter.")
            return
            
        cursor = conn.cursor()
        
        # List all the columns you want to ensure exist in the database
        alter_commands = [
            "ALTER TABLE tool ADD COLUMN category VARCHAR(100) DEFAULT 'Tools'",
            "ALTER TABLE tool ADD COLUMN price DECIMAL(10,2) DEFAULT 0.00",
            "ALTER TABLE tool ADD COLUMN location VARCHAR(100) DEFAULT 'N/A'",
            
            # --- YOUR NEW OMNI-LOG TRACKER COLUMN ---
            "ALTER TABLE tool ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        ]

        print("Executing schema upgrades...")
        
        # Loop through each command individually so a duplicate doesn't stop the script!
        for cmd in alter_commands:
            try:
                cursor.execute(cmd)
                print("✅ Successfully added column!")
            except Exception as e:
                # If the column is already there, just quietly skip it
                if "Duplicate column name" in str(e):
                    print("⏭️ Column already exists, skipping.")
                else:
                    print(f"⚠️ Error: {e}")
        
        conn.commit()
        print("🎉 Database upgrade finished perfectly!")
        
    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        # Safe closure
        if 'conn' in locals() and conn is not None and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    upgrade_database()