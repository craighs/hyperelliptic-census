import sqlite3
import math

def generate_isogeny_classes(q, db_path="gf64_curves_verify.db"):
    """
    Generates the raw Hasse-Weil grid (curves table).
    For q = 64, this generates exactly 5,521 theoretical isogeny targets.
    Geometric exclusions (Serre, Waterhouse, Decomposable) are naturally 
    filtered out during the Phase 1 Cartier-Manin sieve polynomial search.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS curves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        q INTEGER,
        a1 INTEGER,
        a2 INTEGER,
        target_order INTEGER
    )''')
    
    sqrt_q = math.sqrt(q)
    max_a1 = math.floor(4 * sqrt_q)
    
    raw_grid_volume = 0
    
    for a1 in range(-max_a1, max_a1 + 1):
        # Precise Weil bounds for a2 given a1
        min_a2 = math.ceil(2 * sqrt_q * abs(a1)) - 2 * q
        max_a2 = math.floor((a1**2) / 4.0) + 2 * q
        
        for a2 in range(min_a2, max_a2 + 1):
            
            # Calculate Theoretical Geometric Group Order N
            target_order = (q**2) + 1 + a1 * (q + 1) + a2
            
            # Insert the raw theoretical target directly into the database
            cursor.execute('''INSERT INTO curves (q, a1, a2, target_order)
                              VALUES (?, ?, ?, ?)''', (q, a1, a2, target_order))
            raw_grid_volume += 1
            
    conn.commit()
    conn.close()
    print(f"Raw Hasse-Weil Grid Volume generated: {raw_grid_volume} curves.")

if __name__ == "__main__":
    generate_isogeny_classes(32, db_path="verify_gf32_curves.db")
