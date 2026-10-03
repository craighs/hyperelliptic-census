import sqlite3
import os

def cross_check_curves(q, master_db="gf_master.db", verify_db=None):
    if verify_db is None:
        verify_db = f"verify_gf{q}_curves.db"
        
    if not os.path.exists(master_db) or not os.path.exists(verify_db):
        print(f"Missing database files for q={q}. Check paths.")
        return

    # Extract coordinates from Master
    master_conn = sqlite3.connect(master_db)
    master_cur = master_conn.cursor()
    master_cur.execute("SELECT a1, a2 FROM curves WHERE q = ?", (q,))
    master_set = set(master_cur.fetchall())
    master_conn.close()

    # Extract coordinates from Verify
    verify_conn = sqlite3.connect(verify_db)
    verify_cur = verify_conn.cursor()
    verify_cur.execute("SELECT a1, a2 FROM curves")
    verify_set = set(verify_cur.fetchall())
    verify_conn.close()

    # Audit Results
    print(f"--- AUDIT REPORT: F_{q} ---")
    print(f"Master Database Count:  {len(master_set)}")
    print(f"Verify Database Count:  {len(verify_set)}")
    
    if master_set == verify_set:
        print("VERDICT: PERFECT MATCH. The Hasse-Weil grids are identical.\n")
    else:
        print("VERDICT: DISCREPANCY DETECTED!")
        missing_in_master = verify_set - master_set
        missing_in_verify = master_set - verify_set
        
        if missing_in_master:
            print(f"Found {len(missing_in_master)} coordinates in Verify that are MISSING in Master.")
            print("Sample:", list(missing_in_master)[:5])
            
        if missing_in_verify:
            print(f"Found {len(missing_in_verify)} coordinates in Master that are MISSING in Verify.")
            print("Sample:", list(missing_in_verify)[:5])
        print("\n")

# Run the audit for q = 2, 4, 8, 16, 32, 64
for k in range(1, 7):
    q_val = 2**k
    # Make sure you've run the generate_isogeny_classes() script for these fields first!
    if os.path.exists(f"verify_gf{q_val}_curves.db"):
        cross_check_curves(q_val)
    else:
        print(f"verify_gf{q_val}_curves.db not found. Run generation script first.\n")
