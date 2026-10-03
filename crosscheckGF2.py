import sqlite3

q = 2
target_a1 = 1
target_a2 = 2

# 1. Fetch from Master DB
master_conn = sqlite3.connect("gf_master.db")
master_cur = master_conn.cursor()
master_cur.execute("""
    SELECT e.h_poly, e.f_poly 
    FROM explicit_curves e
    JOIN curves c ON e.id = c.id
    WHERE c.q = ? AND c.a1 = ? AND c.a2 = ?
""", (q, target_a1, target_a2))
master_set = set(master_cur.fetchall())
master_conn.close()

# 2. Fetch from Verification DB
verify_conn = sqlite3.connect("verify_gf2_explicit.db")
verify_cur = verify_conn.cursor()
verify_cur.execute("""
    SELECT h_poly, f_poly 
    FROM explicit_curves 
    WHERE q = ? AND a1 = ? AND a2 = ?
""", (q, target_a1, target_a2))
verify_set = set(verify_cur.fetchall())
verify_conn.close()

# 3. Audit
print(f"Master DB Curves for ({target_a1}, {target_a2}): {len(master_set)}")
print(f"Verify DB Curves for ({target_a1}, {target_a2}): {len(verify_set)}")

if master_set == verify_set:
    print("VERDICT: PERFECT MATCH. Explicit polynomials are identical.")
else:
    print("VERDICT: DISCREPANCY DETECTED.")
    print("In Verify, missing from Master:", verify_set - master_set)
    print("In Master, missing from Verify:", master_set - verify_set)
