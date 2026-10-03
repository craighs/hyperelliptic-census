import sqlite3
import time
from sage.all import *

print(">>> SCRIPT STARTED: Updating Jacobian Group Structures for F_64", flush=True)

def update_schema_and_compute():
    db_name = "gf64_curves.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Ensure table has group_order and invariants columns
    cursor.execute("PRAGMA table_info(curves)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'group_order' not in columns:
        cursor.execute("ALTER TABLE curves ADD COLUMN group_order TEXT")
    if 'invariants' not in columns:
        cursor.execute("ALTER TABLE curves ADD COLUMN invariants TEXT")
    conn.commit()
    
    cursor.execute("SELECT id, a1, a2 FROM curves")
    rows = cursor.fetchall()
    
    print(f"Loaded {len(rows)} records from {db_name}. Computing group orders...", flush=True)
    
    q = 64
    R = PolynomialRing(ZZ, 'T')
    T = R.gen()
    
    updated_batch = []
    start_time = time.time()
    
    for idx, (row_id, a1, a2) in enumerate(rows):
        try:
            poly = T**4 - a1*(T**3) + a2*(T**2) - q*a1*T + q**2
            group_order = int(poly(1))
            
            factors = factor(group_order)
            cyclic_parts = [f"Z/{p**e}Z" for p, e in factors]
            inv_str = " x ".join(cyclic_parts) if cyclic_parts else f"Z/{group_order}Z"
            
            updated_batch.append((str(group_order), inv_str, row_id))
            
            if len(updated_batch) >= 1000:
                cursor.executemany("""
                    UPDATE curves 
                    SET group_order = ?, invariants = ? 
                    WHERE id = ?
                """, updated_batch)
                conn.commit()
                updated_batch = []
                
                elapsed = time.time() - start_time
                print(f"Processed {idx + 1} / {len(rows)} curves... ({elapsed:.1f}s)", flush=True)
                
        except Exception:
            continue
            
    if updated_batch:
        cursor.executemany("""
            UPDATE curves 
            SET group_order = ?, invariants = ? 
            WHERE id = ?
        """, updated_batch)
        conn.commit()
        
    conn.close()
    print(">>> Group structure updates committed successfully.", flush=True)

if __name__ == '__main__':
    update_schema_and_compute()
