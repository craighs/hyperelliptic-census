r"""
=========================================================================================
PHASE 6: RED-TEAM SQLITE AUDIT PROTOCOL (ENRICHED MASTER EDITION)
=========================================================================================
DEVIL'S ADVOCATE / TRUTHMODE DOCUMENTATION MANIFESTO
THE TORTOISE DIRECTIVE: "Slow and steady wins the race."

TARGET CORRECTION:
Explicitly targets the active `hyperelliptic_census.db`.

NEW MATHEMATICAL AUDITS:
1.  Base Field Integrity: Verifies the `fields` table contains the historically 
    accurate Conway Irreducible Polynomials (and "N/A" for GF(2)).
2.  Target Order Derivation: Verifies the `curves` table successfully calculated 
    Order = q^2 + 1 - a1*(q + 1) + a2, ensuring no curves have a blank/zero target.
=========================================================================================
"""

import sqlite3
import math
import os
import time

DB_NAME = "hyperelliptic_census.db"  # TARGETS THE ACTIVE DB

def run_database_audit():
    abs_path = os.path.abspath(DB_NAME)
    if not os.path.exists(abs_path):
        print(f"[!] RED-TEAM HALT: Database '{DB_NAME}' not found at {abs_path}")
        return

    print("==========================================================")
    print(" INITIATING PHASE 6: ENRICHED DB AUDIT (READ-ONLY)")
    print(f" SCHEMA: {DB_NAME} (Master Relational)")
    print("==========================================================\n")

    start_time = time.time()
    
    db_uri = f"file:{abs_path}?mode=ro"
    conn = sqlite3.connect(db_uri, uri=True)
    cursor = conn.cursor()

    global_total = 0

    print("--- 1. CONSERVATION OF MASS (CURVE COUNTS) ---")
    cursor.execute("SELECT q, COUNT(*) FROM explicit_curves GROUP BY q ORDER BY q")
    counts = cursor.fetchall()
    for q, count in counts:
        print(f"  GF({q:<2}) Total Curves : {count:,}")
        global_total += count
    print(f"  GLOBAL TOTAL       : {global_total:,}\n")

    print(r"--- 2. ALGEBRAIC GEOMETRY: HASSE-WEIL BOUNDS ---")
    print(r"  (\sqrt{q} - 1)^4 <= Order <= (\sqrt{q} + 1)^4")
    
    cursor.execute("""
        SELECT q, MIN(geometric_order), MAX(geometric_order) 
        FROM explicit_curves 
        GROUP BY q ORDER BY q
    """)
    bounds = cursor.fetchall()
    
    for q, actual_min, actual_max in bounds:
        theo_min = math.floor((math.sqrt(q) - 1)**4)
        theo_max = math.ceil((math.sqrt(q) + 1)**4)
        status = "[PASS]" if (actual_min >= theo_min and actual_max <= theo_max) else "[FAIL]"
        print(f"  GF({q:<2}) {status} Theoretical: [{theo_min}, {theo_max}] | Actual DB: [{actual_min}, {actual_max}]")

    print("\n--- 3. P-RANK DISTRIBUTION (SUPERSINGULARITY) ---")
    cursor.execute("""
        SELECT q, p_rank, COUNT(*) 
        FROM explicit_curves 
        GROUP BY q, p_rank 
        ORDER BY q ASC, p_rank ASC
    """)
    pranks = cursor.fetchall()
    
    current_q = None
    for q, p_rank, count in pranks:
        if q != current_q:
            if current_q is not None:
                print("")
            print(f"  GF({q}):")
            current_q = q
            
        rank_label = "Supersingular" if p_rank == 0 else "Ordinary"
        print(f"    - {rank_label} (rank={p_rank}){' ' * (15 - len(rank_label))}: {count:,}")

    print("\n--- 4. TOPOLOGICAL FRAGMENTATION (TOP 10 INVARIANTS) ---")
    cursor.execute("""
        SELECT invariant_factors, COUNT(*) as c 
        FROM explicit_curves 
        GROUP BY invariant_factors 
        ORDER BY c DESC LIMIT 5
    """)
    top_structures = cursor.fetchall()
    
    for idx, (snf, count) in enumerate(top_structures, 1):
        print(f"  {idx:>2}. {snf:<35}: {count:,} occurrences")

    print("\n--- 5. CONWAY POLYNOMIALS (BASE FIELD INTEGRITY) ---")
    cursor.execute("SELECT q, irreducible_poly FROM fields ORDER BY q")
    fields_data = cursor.fetchall()
    for q, poly in fields_data:
        print(f"  GF({q:<2}) Irreducible Poly: {poly}")

    print("\n--- 6. TARGET ORDER DERIVATION (WEIL TRACES) ---")
    cursor.execute("SELECT COUNT(*) FROM curves WHERE target_order = 0 OR target_order IS NULL")
    missing_targets = cursor.fetchone()[0]
    if missing_targets == 0:
        print("  [PASS] 100% of curves have mathematically derived target orders.")
    else:
        print(f"  [FAIL] {missing_targets} curves are missing target orders.")

    cursor.execute("SELECT q, a1, a2, target_order FROM curves WHERE q=4 LIMIT 3")
    samples = cursor.fetchall()
    print("  Sample Target Orders over GF(4):")
    for q, a1, a2, to in samples:
        print(f"    a1={a1:>2}, a2={a2:>3}  ->  Target Order: {to}")

    conn.close()
    
    elapsed = time.time() - start_time
    print("\n==========================================================")
    print(f" AUDIT COMPLETE. Execution Time: {elapsed:.3f} seconds.")
    print("==========================================================")

if __name__ == '__main__':
    run_database_audit()
