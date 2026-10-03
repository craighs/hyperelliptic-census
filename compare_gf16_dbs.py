import sqlite3
import sys

def compare_databases(old_db_path, new_db_path):
    print(f"=== COMPARING {old_db_path} AND {new_db_path} ===")
    
    try:
        # Connect to the new database
        conn = sqlite3.connect(new_db_path)
        cursor = conn.cursor()
        
        # Attach the old database to query across both simultaneously
        cursor.execute(f"ATTACH DATABASE '{old_db_path}' AS old_db")
        
        # 1. Total row count comparison
        cursor.execute("SELECT COUNT(*) FROM old_db.explicit_curves")
        old_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM main.explicit_curves")
        new_count = cursor.fetchone()[0]
        
        print(f"Rows in OLD explicit_curves: {old_count}")
        print(f"Rows in NEW explicit_curves: {new_count}")
        
        # 2. Strict Polynomial and Invariant Consistency Check
        # This checks if the exact same h(x), f(x), and invariant factors were found for each ID
        query = """
            SELECT 
                old.id, 
                old.h_poly, new.h_poly,
                old.f_poly, new.f_poly,
                old.invariant_factors, new.invariant_factors
            FROM old_db.explicit_curves old
            JOIN main.explicit_curves new ON old.id = new.id
            WHERE old.h_poly != new.h_poly 
               OR old.f_poly != new.f_poly 
               OR old.invariant_factors != new.invariant_factors
        """
        cursor.execute(query)
        mismatches = cursor.fetchall()
        
        if not mismatches:
            print("\n[PASS] Absolute Consistency: 100% Match.")
            print("       Both algorithms found the exact same polynomials and invariants for every target.")
        else:
            print(f"\n[FAIL] Found {len(mismatches)} discrepancies between the runs:")
            for row in mismatches[:5]: # Print first 5 mismatches
                print(f"  Target ID {row[0]}:")
                if row[1] != row[2]: print(f"    h_poly DIFF: OLD='{row[1]}' | NEW='{row[2]}'")
                if row[3] != row[4]: print(f"    f_poly DIFF: OLD='{row[3]}' | NEW='{row[4]}'")
                if row[5] != row[6]: print(f"    inv DIFF: OLD='{row[5]}' | NEW='{row[6]}'")
            if len(mismatches) > 5:
                print("  ... (output truncated)")

        # 3. Missing Data Check (Did either script miss a target the other found?)
        cursor.execute("SELECT id FROM old_db.explicit_curves WHERE id NOT IN (SELECT id FROM main.explicit_curves)")
        missing_in_new = cursor.fetchall()
        if missing_in_new:
            print(f"\n[!] NEW database is missing {len(missing_in_new)} targets found in OLD database.")
            
        cursor.execute("SELECT id FROM main.explicit_curves WHERE id NOT IN (SELECT id FROM old_db.explicit_curves)")
        missing_in_old = cursor.fetchall()
        if missing_in_old:
            print(f"\n[!] NEW database found {len(missing_in_old)} targets that were missing in OLD database.")

        conn.close()
        
    except sqlite3.Error as e:
        print(f"[!] Database error: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 compare_gf16_dbs.py <old_db.db> <new_db.db>")
        sys.exit(1)
        
    compare_databases(sys.argv[1], sys.argv[2])
