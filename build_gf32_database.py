import sqlite3
import math

def get_hw_bounds(q):
    """Calculates all theoretically valid group orders for Genus 2 over F_q"""
    targets = []
    
    # 1. Bounding the trace over the base field (N1)
    a1_max = math.floor(4 * math.sqrt(q))
    
    for a1 in range(-a1_max, a1_max + 1):
        # 2. Bounding the trace over the extension field (N2)
        # Using the Weil polynomial root bounds for genus 2
        a2_max = math.floor(4 * q + 2 * q - (a1**2) / 2.0)
        a2_min = math.ceil(4 * q - 2 * q - (a1**2) / 2.0)
        
        # Applying the discriminant constraint: 
        # (a1^2 - 4*a2 + 8*q)^2 - 64*q*a1^2 >= 0
        for a2 in range(a2_min, a2_max + 1):
            disc = (a1**2 - 4*a2 + 8*q)**2 - 64*q*(a1**2)
            if disc >= 0:
                # 3. Calculate Group Order
                N = q**2 + 1 - (q + 1) * a1 + a2
                targets.append((N, a1, a2))
                
    # Deduplicate and sort by group order
    return sorted(list(set(targets)), key=lambda x: x[0])

if __name__ == "__main__":
    db_name = "gf32_curves.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Standardized Schema matching GF64
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS curves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_order INTEGER NOT NULL,
            a1 INTEGER,
            a2 INTEGER,
            field_size INTEGER DEFAULT 32
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
    
    # Check if table is empty before inserting
    cursor.execute("SELECT COUNT(*) FROM curves")
    if cursor.fetchone()[0] == 0:
        targets = get_hw_bounds(32)
        print(f"Generated {len(targets)} theoretical Hasse-Weil targets for GF(32).")
        
        cursor.executemany(
            "INSERT INTO curves (group_order, a1, a2) VALUES (?, ?, ?)",
            targets
        )
        conn.commit()
        print("Database populated successfully.")
    else:
        print("Database already populated.")
        
    conn.close()
