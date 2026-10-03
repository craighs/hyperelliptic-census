import sqlite3
import csv
import ast

def create_lmfdb_database(db_path="hyperelliptic_census.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS fields (
                        q INTEGER PRIMARY KEY,
                        k INTEGER,
                        irreducible_poly TEXT
                      )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS curves (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        q INTEGER,
                        a1 INTEGER,
                        a2 INTEGER,
                        target_order INTEGER,
                        UNIQUE(q, a1, a2),
                        FOREIGN KEY(q) REFERENCES fields(q)
                      )''')
                      
    cursor.execute('''CREATE TABLE IF NOT EXISTS explicit_curves (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        curve_id INTEGER,
                        q INTEGER,
                        h_poly_coeffs TEXT,
                        f_poly_coeffs TEXT,
                        h_poly_str TEXT,
                        f_poly_str TEXT,
                        geometric_order INTEGER,
                        invariant_factors TEXT,
                        FOREIGN KEY(curve_id) REFERENCES curves(id),
                        FOREIGN KEY(q) REFERENCES fields(q)
                      )''')
                      
    conn.commit()
    return conn

def format_readable_poly(coeffs_str, q, var='x', prim='z'):
    """Translates a Zech-log array string into a human-readable polynomial."""
    coeffs = ast.literal_eval(coeffs_str)
    terms = []
    for deg, exp in enumerate(coeffs):
        if exp == -1: continue
        
        if q == 2:
            c_str = "" # Coefficient is implicitly 1
        else:
            if exp == 0: c_str = ""
            elif exp == 1: c_str = prim
            else: c_str = f"{prim}^{exp}"
        
        if deg == 0:
            x_str = ""
            if c_str == "": c_str = "1"
        elif deg == 1:
            x_str = var
        else:
            x_str = f"{var}^{deg}"
        
        if c_str and x_str:
            term = f"{c_str}*{x_str}"
        else:
            term = f"{c_str}{x_str}"
        terms.append(term)
        
    if not terms: return "0"
    return " + ".join(reversed(terms))

def populate_database(conn):
    cursor = conn.cursor()
    
    bases = {
        2: "N/A (Prime Field)",
        4: "x^2 + x + 1",
        8: "x^3 + x + 1",
        16: "x^4 + x + 1",
        32: "x^5 + x^2 + 1",
        64: "x^6 + x^4 + x^3 + x + 1"
    }
    
    for q, poly in bases.items():
        k = q.bit_length() - 1
        cursor.execute('INSERT OR IGNORE INTO fields (q, k, irreducible_poly) VALUES (?, ?, ?)', (q, k, poly))
    
    isogeny_cache = {} 
    
    for q in [2, 4, 8, 16, 32, 64]:
        filename = f"gf{q}_jacobian_groups_repaired.csv"
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    T = int(row['target_order'])
                    geom = int(row['geometric_order'])
                    L = geom // T
                    
                    a1 = (T - L) // (2 * q + 2)
                    a2 = (T + L - 2 - 2 * q**2) // 2
                    
                    iso_key = (q, a1, a2)
                    if iso_key not in isogeny_cache:
                        cursor.execute('''INSERT INTO curves (q, a1, a2, target_order)
                                          VALUES (?, ?, ?, ?)''', (q, a1, a2, T))
                        isogeny_cache[iso_key] = cursor.lastrowid
                        
                    curve_id = isogeny_cache[iso_key]
                    
                    inv_factors = row['abelian_group_structure']
                    h_coeffs = row['h_coeffs']
                    f_coeffs = row['f_coeffs']
                    
                    h_str = format_readable_poly(h_coeffs, q)
                    f_str = format_readable_poly(f_coeffs, q)
                    
                    cursor.execute('''INSERT INTO explicit_curves 
                                      (curve_id, q, h_poly_coeffs, f_poly_coeffs, h_poly_str, f_poly_str, geometric_order, invariant_factors)
                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                                   (curve_id, q, h_coeffs, f_coeffs, h_str, f_str, geom, inv_factors))
        except FileNotFoundError:
            pass
            
    conn.commit()
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_curves_q ON curves(q)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_explicit_curve_id ON explicit_curves(curve_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_explicit_q ON explicit_curves(q)')
    conn.commit()

if __name__ == '__main__':
    db_conn = create_lmfdb_database("hyperelliptic_census.db")
    populate_database(db_conn)
    db_conn.close()
