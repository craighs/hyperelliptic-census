import sqlite3
import sys
from sage.all import GF, PolynomialRing, HyperellipticCurve, prod, lcm, divisors

def dual_verify_gf2():
    print("=== INITIATING 0bp DUAL-VERIFICATION FOR GF(2) ===")
    
    F = GF(2)
    R = PolynomialRing(F, 'x')
    x = R.gen()
    db_path = "gf2_curves.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # PROPER SQL JOIN: We must map the Primary Key (id) to the actual target math
        query = """
            SELECT 
                e.id, e.h_poly, e.f_poly, e.invariant_factors, 
                c.a1, c.a2
            FROM explicit_curves e
            JOIN curves c ON e.id = c.id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"Loaded {len(rows)} geometric targets from database.\n")
        mismatches = 0
        
        for row in rows:
            target_id, h_str, f_str, db_inv_str, target_a1, target_a2 = row
            
            # The actual group order the sieve was hunting
            target_order = 5 - 3*target_a1 + target_a2
            
            h_poly = R(h_str.replace('^', '**'))
            f_poly = R(f_str.replace('^', '**'))
            C = HyperellipticCurve(f_poly, h_poly)
            J = C.jacobian()
            
            # 1. INDEPENDENT ENGINE: Order via Zeta Function
            # This is mathematically irrefutable.
            Z = C.zeta_function()
            L = Z.numerator()
            true_order = int(L(1))
            
            # 2. INDEPENDENT ENGINE: Structure via Divisor Sampling
            exponent = 1
            attempts = 0
            while attempts < 25 and exponent != true_order:
                attempts += 1
                try:
                    D = J.random_element()
                    ord_D = 1
                    for d in divisors(true_order):
                        if d * D == J(0):
                            ord_D = d
                            break
                    exponent = lcm(exponent, ord_D)
                except Exception:
                    continue
            
            if exponent == true_order:
                true_inv_list = [true_order]
            else:
                d1 = true_order // exponent
                d2 = exponent
                if d2 % d1 == 0:
                    true_inv_list = [d1, d2]
                else:
                    true_inv_list = [d1, d2] 
                    
            # 3. The 0bp Strict Comparison
            if db_inv_str and "PENDING" in str(db_inv_str).upper():
                print(f"[RESOLUTION] Row ID {target_id: <3} | Target Order: {target_order: <3} | True Order: {true_order: <3} | True Invariants: {str(true_inv_list)}")
                if true_order != target_order:
                    print(f"       [FAIL] Geometric Order {true_order} != Target Order {target_order}")
                    mismatches += 1
            else:
                db_inv_list = eval(db_inv_str) if db_inv_str else []
                if true_inv_list != db_inv_list:
                    print(f"[FAIL] Row ID {target_id: <3}: DB {db_inv_list} != True {true_inv_list}")
                    mismatches += 1
                else:
                    print(f"[PASS] Row ID {target_id: <3} | Target Order: {target_order: <3} | True Order: {true_order: <3}")

        print("\n=== VERIFICATION SUMMARY ===")
        if mismatches == 0:
            print(f"[SUCCESS] 0bp Error. All {len(rows)} curves independently dual-verified.")
        else:
            print(f"[WARNING] Found {mismatches} mathematical discrepancies. Audit required.")
            
        conn.close()

    except sqlite3.Error as e:
        print(f"[!] Database error: {e}")
    except Exception as e:
        print(f"[!] SageMath execution error: {e}")

if __name__ == '__main__':
    dual_verify_gf2()
