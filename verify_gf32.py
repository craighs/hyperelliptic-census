import sqlite3
import sys

def verify_gf32_environment():
    db_name = "gf32_curves.db"
    print(f"=== 1. DATABASE SCHEMA AUDIT ({db_name}) ===")
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # 1. Audit 'curves' table
        cursor.execute("PRAGMA table_info(curves)")
        curves_cols = {row[1]: row for row in cursor.fetchall()}
        
        if not curves_cols:
            print("[FAIL] 'curves' table is missing entirely.")
        else:
            print("[PASS] 'curves' table exists.")
            if 'a1' in curves_cols:
                print("[PASS] 'a1' column found in 'curves'.")
                # Verify a1 actually contains data, not just NULLs
                cursor.execute("SELECT COUNT(*) FROM curves WHERE a1 IS NOT NULL")
                a1_count = cursor.fetchone()[0]
                if a1_count > 0:
                    print(f"       -> {a1_count} rows have valid 'a1' data.")
                else:
                    print("[FAIL] 'a1' column exists but contains NO data. Sieve will discard all curves.")
            else:
                print("[FAIL] 'a1' column is missing. Sieve will hard crash.")

        # 2. Audit 'explicit_curves' table
        cursor.execute("PRAGMA table_info(explicit_curves)")
        explicit_cols = {row[1] for row in cursor.fetchall()}
        required = {'id', 'h_poly', 'f_poly', 'invariant_factors'}
        
        if not explicit_cols:
            print("[FAIL] 'explicit_curves' table is missing entirely.")
        else:
            missing = required - explicit_cols
            if missing:
                print(f"[FAIL] 'explicit_curves' is missing required columns: {missing}")
            else:
                print("[PASS] 'explicit_curves' schema is compatible.")
                
        conn.close()
        
    except sqlite3.Error as e:
        print(f"[!] Database connection error: {e}")

    print("\n=== 2. SAGEMATH EXTENSION FIELD AUDIT (GF(32) -> GF(1024)) ===")
    
    try:
        from sage.all import GF
        # F_32 is an odd extension (2^5)
        F = GF(32, 'z')
        # F_1024 is an even extension (2^10)
        F2 = GF(1024, 'w')
        
        mod_coeffs_F2 = [F2(int(c)) for c in F.modulus().list()]
        
        r = None
        for w in list(F2):
            if sum((c * (w**i) for i, c in enumerate(mod_coeffs_F2)), F2(0)) == F2(0):
                r = w
                break
                
        if r is not None:
            print(f"[PASS] Successfully mapped GF(32) modulus to GF(1024) root: {r}")
        else:
            print("[FAIL] Failed to find root mapping. SageMath generated incompatible polynomials.")
            
    except Exception as e:
        print(f"[!] SageMath execution error: {e}")

if __name__ == '__main__':
    verify_gf32_environment()
