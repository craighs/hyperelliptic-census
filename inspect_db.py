import sqlite3

db_path = "Unique_GF32.db"
print(f"=== Inspecting Schema for {db_path} ===")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Extract all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if not tables:
        print("Database is empty or invalid.")
    else:
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            
            # Extract column names for this table
            cursor.execute(f"PRAGMA table_info('{table_name}');")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
                
    conn.close()
except sqlite3.OperationalError as e:
    print(f"Failed to open database: {e}")
