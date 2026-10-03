r"""
=========================================================================================
PHASE 4: RED-TEAM SQLITE INGESTION PROTOCOL (MASTER SCHEMA EDITION)
=========================================================================================
DEVIL'S ADVOCATE / TRUTHMODE DOCUMENTATION MANIFESTO
THE TORTOISE DIRECTIVE: "Slow and steady wins the race."

TARGET OPERATIONAL DATABASE:
Explicitly targets the active `hyperelliptic_census.db`, completely isolating and 
protecting the historical `_father.db` backup file.

MATHEMATICAL & HISTORICAL ENRICHMENTS:
1. Conway Polynomials (Historical Parity): 
   Injects standard SageMath Conway irreducible polynomials into the `fields` table.
   Crucially, GF(2) is historically and mathematically mapped to "N/A (Prime Field)" 
   because it is the base field and requires no polynomial extension.

2. Target Order Derivation (Characteristic Polynomial of Frobenius):
   Calculates the theoretical Jacobian group order directly from the Weil 
   polynomial traces (a1, a2). For a genus 2 curve over GF(q), the characteristic 
   polynomial evaluates at 1 to yield the exact order:
   Order = q^2 + 1 - a1*(q + 1) + a2

3. Supersingularity (p-rank):
   Extracts the degree of the h(x) polynomial dynamically. If deg(h) == 0, the 
   curve has a p-rank of 0, proving supersingularity (trivial p-torsion).

OPERATIONAL SAFEGUARDS:
- PRAGMA foreign_keys = ON enforced for strict schema topology.
- WAL journal mode and batch transactions (10,000 row limits) for memory safety.
- In-memory hash maps for `fields` and `curves` to prevent N+1 I/O thrashing.
=========================================================================================
"""

import sqlite3
import csv
import os
import time
import ast
import math

TARGET_FIELDS = [2, 4, 8, 16, 32, 64]
DB_NAME = "hyperelliptic_census.db"
BATCH_SIZE = 10000

# SageMath default Conway Irreducible Polynomials for GF(2^k)
# Historically verified against father.db baseline (2026-10-02)
CONWAY_POLYS = {
    2: "N/A (Prime Field)", 
    4: "x^2 + x + 1",
    8: "x^3 + x + 1",
    16: "x^4 + x + 1",
    32: "x^5 + x^2 + 1",
    64: "x^6 + x^4 + x^3 + x + 1"
}

def coeffs_to_poly_string(coeffs_string):
    """
    Translates characteristic 2 Zech log arrays into human-readable polynomials.
    In Char 2: -1 means 0. Any other integer represents a coefficient α^i.
    Formats coefficients as (a^i)*x^k for visual mathematical auditing.
    """
    try:
        coeffs = ast.literal_eval(coeffs_string)
        terms = []
        for power, coeff in enumerate(coeffs):
            if coeff != -1:
                # Format the coefficient
                if coeff == 0:
                    c_str = "" # a^0 is 1
                else:
                    c_str = f"(a^{coeff})"
                
                # Format the variable
                if power == 0:
                    v_str = "1" if c_str == "" else ""
                elif power == 1:
                    v_str = "x"
                else:
                    v_str = f"x^{power}"
                
                terms.append(f"{c_str}{v_str}")
        
        if not terms:
            return "0"
        return " + ".join(reversed(terms))
    except Exception:
        return "ERROR"

def get_polynomial_degree(coeffs_string):
    """
    Derives p-rank dynamically. The p-rank in char 2 is exactly the degree of h(x).
    Returns 0 if h(x) is a constant (Supersingular curve).
    """
    try:
        coeffs = ast.literal_eval(coeffs_string)
        for i in range(len(coeffs) - 1, -1, -1):
            if coeffs[i] != -1:
                return i
        return 0
    except Exception:
        return 0

def create_schema(cursor):
    """Enforces strict SQLite normalized relational typologies."""
    print(f"[*] Enforcing Master 3-Table Relational Schema into {DB_NAME}...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fields (
            q INTEGER PRIMARY KEY,
            k INTEGER,
            irreducible_poly TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS curves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            q INTEGER,
            a1 INTEGER,
            a2 INTEGER,
            target_order INTEGER,
            UNIQUE(q, a1, a2),
            FOREIGN KEY(q) REFERENCES fields(q)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS explicit_curves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            curve_id INTEGER,
            q INTEGER,
            h_poly_coeffs TEXT,
            f_poly_coeffs TEXT,
            h_poly_str TEXT,
            f_poly_str TEXT,
            geometric_order INTEGER,
            p_rank INTEGER,
            invariant_factors TEXT,
            FOREIGN KEY(curve_id) REFERENCES curves(id),
            FOREIGN KEY(q) REFERENCES fields(q)
        )
    ''')

def generate_indexes(cursor):
    print("[*] Generating Foreign Key and Query Indexes...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_curves_q ON curves(q)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_explicit_curve_id ON explicit_curves(curve_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_explicit_q ON explicit_curves(q)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_explicit_order ON explicit_curves(geometric_order)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_explicit_prank ON explicit_curves(p_rank)')

def ingest_data():
    if os.path.exists(DB_NAME):
        print(f"[!] Purging existing database {DB_NAME} to guarantee execution integrity.")
        os.remove(DB_NAME)
        
    conn = sqlite3.connect(DB_NAME, isolation_level=None)
    cursor = conn.cursor()
    
    # Red-Team Operational Optimizations
    cursor.execute('PRAGMA journal_mode = WAL;')
    cursor.execute('PRAGMA synchronous = NORMAL;')
    cursor.execute('PRAGMA foreign_keys = ON;')
    
    create_schema(cursor)
    
    total_inserted = 0
    start_time = time.time()

    # In-memory caches to prevent N+1 DB thrashing
    known_fields = set()
    curve_cache = {}

    for field_size in TARGET_FIELDS:
        csv_file = f"gf{field_size}_jacobian_groups.csv"
        if not os.path.exists(csv_file):
            print(f"[!] SKIP: {csv_file} not found.")
            continue
            
        print(f"[*] Relational Ingestion for GF({field_size}) -> {csv_file}")
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            
            cursor.execute('BEGIN TRANSACTION;')
            
            batch = []
            for row in reader:
                # 1. Map Core Variables
                q = int(row.get('q', field_size))
                a1 = int(row.get('a1', 0))
                a2 = int(row.get('a2', 0))
                geom_order = int(row.get('base_field_order', 0))
                
                h_coeffs_str = row.get('h_coeffs', '[]')
                f_coeffs_str = row.get('f_coeffs', '[]')
                snf_str = row.get('abelian_group_structure', 'UNKNOWN')
                
                # 2. Field Table Maintenance (Enriched with Conway Polynomials)
                if q not in known_fields:
                    k = int(math.log2(q)) if q > 0 else 0
                    irr_poly = CONWAY_POLYS.get(q, "UNKNOWN")
                    cursor.execute('INSERT OR IGNORE INTO fields (q, k, irreducible_poly) VALUES (?, ?, ?)', (q, k, irr_poly))
                    known_fields.add(q)
                
                # 3. Curve (Parent) Table Maintenance (Enriched with Target Order Derivation)
                curve_key = (q, a1, a2)
                if curve_key not in curve_cache:
                    # Mathematical derivation of Jacobian order via characteristic polynomial
                    # Target Order = q^2 + 1 - a1*(q + 1) + a2
                    target_order = (q**2) + 1 - (a1 * (q + 1)) + a2
                    
                    cursor.execute('''
                        INSERT OR IGNORE INTO curves (q, a1, a2, target_order)
                        VALUES (?, ?, ?, ?)
                    ''', (q, a1, a2, target_order))
                    
                    cursor.execute('SELECT id FROM curves WHERE q=? AND a1=? AND a2=?', (q, a1, a2))
                    curve_id = cursor.fetchone()[0]
                    curve_cache[curve_key] = curve_id
                else:
                    curve_id = curve_cache[curve_key]
                
                # 4. Derive Polynomial Strings and p-rank
                h_str = coeffs_to_poly_string(h_coeffs_str)
                f_str = coeffs_to_poly_string(f_coeffs_str)
                p_rank = get_polynomial_degree(h_coeffs_str)
                
                # 5. Pack Explicit Curve
                batch.append((
                    curve_id,
                    q,
                    h_coeffs_str,
                    f_coeffs_str,
                    h_str,
                    f_str,
                    geom_order,
                    p_rank,
                    snf_str
                ))
                
                if len(batch) >= BATCH_SIZE:
                    cursor.executemany('''
                        INSERT INTO explicit_curves (
                            curve_id, q, h_poly_coeffs, f_poly_coeffs, 
                            h_poly_str, f_poly_str, geometric_order, p_rank, invariant_factors
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', batch)
                    total_inserted += len(batch)
                    batch = []
                    
            if batch:
                cursor.executemany('''
                    INSERT INTO explicit_curves (
                        curve_id, q, h_poly_coeffs, f_poly_coeffs, 
                        h_poly_str, f_poly_str, geometric_order, p_rank, invariant_factors
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', batch)
                total_inserted += len(batch)
                
            cursor.execute('COMMIT;')
            print(f"  -> Successfully committed GF({field_size}).")

    generate_indexes(cursor)
    
    print("\n[*] Vacuuming Database...")
    cursor.execute('VACUUM;')
    conn.close()
    
    elapsed = time.time() - start_time
    print("==========================================================")
    print(f" RELATIONAL INGESTION COMPLETE: {total_inserted:,} curves secured.")
    print(f" Target Database: {DB_NAME}")
    print(f" Execution Time: {elapsed:.2f} seconds.")
    print("==========================================================")

if __name__ == '__main__':
    ingest_data()
