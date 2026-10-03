import sqlite3
import math
import sys

def get_hw_bounds(q):
    targets = []
    a1_max = math.floor(4 * math.sqrt(q))
    for a1 in range(-a1_max, a1_max + 1):
        # TRUE HASSE-WEIL BOUNDS
        a2_min = math.ceil(2 * math.sqrt(q) * abs(a1) - 2 * q)
        a2_max = math.floor((a1**2) / 4.0 + 2 * q)
        
        for a2 in range(a2_min, a2_max + 1):
            N = q**2 + 1 - (q + 1) * a1 + a2
            targets.append((N, a1, a2))
    return sorted(list(set(targets)), key=lambda x: x[0])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 build_db.py <Q>")
        
    Q = int(sys.argv[1])
    db_name = f"gf{Q}_curves.db"
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS curves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_order INTEGER NOT NULL,
            a1 INTEGER,
            a2 INTEGER,
            field_size INTEGER DEFAULT {Q}
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS explicit_curves (
            id INTEGER PRIMARY KEY,
            h_poly TEXT NOT NULL,
            f_poly TEXT NOT NULL,
            invariant_factors TEXT DEFAULT 'PENDING',
            FOREIGN KEY(id) REFERENCES curves(id)
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM curves")
    if cursor.fetchone()[0] == 0:
        targets = get_hw_bounds(Q)
        cursor.executemany("INSERT INTO curves (group_order, a1, a2) VALUES (?, ?, ?)", targets)
        conn.commit()
        print(f"[+] Generated {len(targets)} theoretical targets for GF({Q}) in {db_name}")
    else:
        print(f"[!] Database {db_name} already populated.")
        
    conn.close()
