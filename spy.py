from database import get_connection

def inspect_database():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("\n=== YOUR TABLES ===")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if not tables:
            print("Your database is completely empty! You need to create your tables.")
            return

        for table in tables:
            table_name = table[0]
            print(f"\n📁 Table: {table_name}")
            print("-" * 30)
            
            # Get columns for each table
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = cursor.fetchall()
            for col in columns:
                col_name = col[0]
                col_type = col[1]
                print(f"  ↳ {col_name} ({col_type})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    inspect_database()