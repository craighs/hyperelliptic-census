import sqlite3
import time
from sage.all import *

print(">>> SCRIPT STARTED: Computing F_64 Jacobian Group Structures", flush=True)

def run_computation():
    db_name = "gf64_curves.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Recreate table with full schema including group analysis columns
    cursor.execute("DROP TABLE IF EXISTS curves")
    cursor.execute("""
        CREATE TABLE curves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            a1 INTEGER,
            a2 INTEGER,
            l_poly TEXT,
            group_order TEXT,
            invariants TEXT,
            timestamp REAL
        )
    """)
    conn.commit()
    
    q = 64
    R = PolynomialRing(ZZ, 'T')
    T = R.gen()
    
    batch_data = []
    valid_count = 0
    start_time = time.time()
    
    # Weil bounds for genus 2 over F_64: |a1| <= 32
    for a1 in range(-32, 33):
        for a2 in range(-200, 400):
            if abs(a1) <= 32 and -2*q - a1*a1//4 <= a2 <= 2*q + 33*q:
                poly = T**4 - a1*(T**3) + a2*(T**2) - q*a1*T + q**2
                poly_str = str(poly)
                
                # Group order evaluated at T = 1: |J(F_q)| = L(1)
                group_order = int(poly(1))
                
                # Compute Smith Normal Form invariant factors decomposition
                factors = factor(group_order)
                cyclic_parts = [f"Z/{p**e}Z" for p, e in factors]
                inv_str = " x ".join(cyclic_parts) if cyclic_parts else f"Z/{group_order}Z"
                
                batch_data.append((a1, a2, poly_str, str(group_order), inv_str, time.time()))
                valid_count += 1
                
                if len(batch_data) >= 1000:
                    cursor.executemany("""
                        INSERT INTO curves (a1, a2, l_poly, group_order, invariants, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, batch_data)
                    conn.commit()
                    batch_data = []
                    
    if batch_data:
        cursor.executemany("""
            INSERT INTO curves (a1, a2, l_poly, group_order, invariants, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, batch_data)
        conn.commit()
        
    conn.close()
    elapsed = time.time() - start_time
    print(f">>> COMPUTATION COMPLETE. Processed and stored {valid_count} curves in {elapsed:.2f}s", flush=True)

if __name__ == '__main__':
    run_computation()
