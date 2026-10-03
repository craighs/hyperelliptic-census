import sqlite3
import sys
from sage.all import GF, PolynomialRing, sage_eval

def verify_db(Q):
    db_name = f"gf{Q}_curves.db"
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT e.id, c.group_order, e.h_poly, e.f_poly FROM curves c JOIN explicit_curves e ON c.id = e.id")
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        sys.exit(f"Could not read {db_name}: {e}")

    if not rows:
        sys.exit(f"No explicit curves found in {db_name}")

    print(f"=== ANCHOR TEST: Naive Brute Force Point Counting for GF({Q}) ===")
    print(f"Verifying {len(rows)} explicitly matched curves...\n")

    F = GF(Q, 'z')
    F2 = GF(Q**2, 'w')
    R_F = PolynomialRing(F, 'x')
    R_F2 = PolynomialRing(F2, 'x')
    
    x_sym = R_F.gen()
    z_sym = F.gen()

    # Explicit Galois Embedding to map 'z' coefficients to 'w' coefficients
    mod_coeffs_F2 = [F2(int(c)) for c in F.modulus().list()]
    r = None
    for w_elem in F2:
        if sum((c * (w_elem**i) for i, c in enumerate(mod_coeffs_F2)), F2(0)) == F2(0):
            r = w_elem
            break
            
    def embed(elem):
        coeffs = elem.polynomial().list()
        return sum((F2(int(a)) * (r**i) for i, a in enumerate(coeffs)), F2(0))

    mismatches = 0
    tested = 0

    for row_id, db_N, h_str, f_str in rows:
        # Safely parse the strings using sage_eval to recognize 'z' and 'x'
        h = R_F(sage_eval(h_str, locals={'x': x_sym, 'z': z_sym}))
        f = R_F(sage_eval(f_str, locals={'x': x_sym, 'z': z_sym}))
        
        # Safely embed the F_q polynomial into F_q^2
        h2 = R_F2([embed(c) for c in h.list()])
        f2 = R_F2([embed(c) for c in f.list()])

        # 1. NAIVE COUNT IN F_Q
        N1 = 1
        for x_val in F:
            hx = h(x_val)
            fx = f(x_val)
            for y_val in F:
                if y_val**2 + hx*y_val == fx:
                    N1 += 1

        # 2. NAIVE COUNT IN F_Q^2
        N2 = 1
        for x_val in F2:
            hx = h2(x_val)
            fx = f2(x_val)
            for y_val in F2:
                if y_val**2 + hx*y_val == fx:
                    N2 += 1

        # 3. HASSE-WEIL JACOBIAN FORMULA (Pure Arithmetic)
        a1 = Q + 1 - N1
        a2 = (N2 - Q**2 - 1 + a1**2) // 2
        N_calculated = Q**2 + 1 - (Q + 1)*a1 + a2

        if N_calculated != db_N:
            print(f"[CRITICAL FAILURE] Curve ID {row_id}")
            print(f"  Sieve claimed N = {db_N}, Brute force says N = {N_calculated}")
            mismatches += 1
        
        tested += 1

    if mismatches == 0:
        print(f"[VERDICT: IRONCLAD] All {tested} curves cryptographically match.")
    else:
        print(f"\n[DEVIL'S ADVOCATE] Found {mismatches} mismatches.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: sage naive_anchor.py <Q>")
    else:
        verify_db(int(sys.argv[1]))
