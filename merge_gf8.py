import sqlite3
import os

MASTER_DB = "GF8_master.db"

def merge_databases():
    print(f"Creating master database: {MASTER_DB}")
    
    # Connect to the new master database (will create it if it doesn't exist)
    master_conn = sqlite3.connect(MASTER_DB)
    master_cursor = master_conn.cursor()

    # Create the table schema exactly as it exists in the parts
    master_cursor.execute("""
        CREATE TABLE IF NOT EXISTS hyperelliptic_curves (
            id INTEGER PRIMARY KEY,
            curve_id VARCHAR NOT NULL UNIQUE,
            isogeny_class VARCHAR NOT NULL,
            f_poly VARCHAR,
            h_poly VARCHAR,
            jacobian_points INTEGER,
            data BLOB
        )
    """)
    master_cursor.execute("CREATE INDEX IF NOT EXISTS ix_isogeny_class ON hyperelliptic_curves (isogeny_class);")
    master_conn.commit()

    total_inserted = 0

    # Loop through all 8 expected part files
    for i in range(8):
        part_db = f"GF8_part_{i}.db"
        
        if not os.path.exists(part_db):
            print(f"Warning: {part_db} not found. Skipping.")
            continue
            
        print(f"Attaching and merging {part_db}...")
        
        # Attach the part database directly to the master connection
        master_cursor.execute(f"ATTACH DATABASE '{part_db}' AS part_db")
        
        # Insert everything from the part into the master (ignoring the auto-increment 'id' column)
        master_cursor.execute("""
            INSERT INTO hyperelliptic_curves (curve_id, isogeny_class, f_poly, h_poly, jacobian_points, data)
            SELECT curve_id, isogeny_class, f_poly, h_poly, jacobian_points, data 
            FROM part_db.hyperelliptic_curves
        """)
        
        inserted_this_round = master_cursor.rowcount
        total_inserted += inserted_this_round
        print(f"  -> Added {inserted_this_round} curves.")
        
        master_conn.commit()
        master_cursor.execute("DETACH DATABASE part_db")

    master_conn.close()
    
    print("-" * 40)
    print("Merge Complete!")
    print(f"Total curves in master database: {total_inserted}")

if __name__ == "__main__":
    merge_databases()
