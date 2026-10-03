import sqlite3
import os

databases = {
    "Unique_GF32.db": 32,
    "Unique_GF16.db": 16,
    "Unique_GF8.db": 8,
    "Unique_GF4.db": 4,
    "Unique_GF2.db": 2
}

def update_database(db_name, q):
    if not os.path.exists(db_name):
        print(f"Skipping {db_name} - file not found.")
        return
        
    print(f"Processing {db_name} (q={q})...")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # 1. Add missing LMFDB columns
    for col in ["a1 INTEGER", "a2 INTEGER", "invariant_factors TEXT"]:
        try:
            cursor.execute(f"ALTER TABLE hyperelliptic_curves ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass # Column already exists

    # 2. Extract and update a1 and a2
    cursor.execute("SELECT id, isogeny_class FROM hyperelliptic_curves WHERE a1 IS NULL")
    rows = cursor.fetchall()
    
    update_data = []
    for row_id, isogeny_class in rows:
        try:
            n1_str, n_str = isogeny_class.split('_')
            N1 = int(n1_str)
            N = int(n_str)
            
            a1 = q + 1 - N1
            a2 = N - q**2 - 1 + a1*(q + 1)
            
            update_data.append((a1, a2, row_id))
        except Exception as e:
            print(f"  Error parsing row {row_id} ({isogeny_class}): {e}")
            
    if update_data:
        cursor.executemany("UPDATE hyperelliptic_curves SET a1=?, a2=? WHERE id=?", update_data)
        conn.commit()
        print(f"  -> Updated {len(update_data)} rows with Weil coefficients (a1, a2).")
    else:
        print("  -> Weil coefficients already up to date.")
        
    conn.close()

for db, q in databases.items():
    update_database(db, q)

print("\nPhase 1 Complete: All databases have a1 and a2 coefficients extracted.")
