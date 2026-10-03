import sqlite3
import math
from sage.all import ZZ

def generate_isogeny_classes(q, db_path="gf_curves_verify.db"):
    """
    Generates all valid genus 2 isogeny class targets (the curves table)
    for a given finite field size q = 2^k. Applies Hasse-Weil bounds,
    Decomposable surface exclusions, Waterhouse Newton polygon constraints,
    and Serre's point-counting defects.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the curves table matching our unified master schema
    cursor.execute('''CREATE TABLE IF NOT EXISTS curves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        q INTEGER,
        a1 INTEGER,
        a2 INTEGER,
        target_order INTEGER
    )''')
    
    k = int(math.log2(q))
    sqrt_q = math.sqrt(q)
    
    # Bounding a1: |a1| <= floor(4 * sqrt(q))
    max_a1 = math.floor(4 * sqrt_q)
    
    valid_count = 0
    
    for a1 in range(-max_a1, max_a1 + 1):
        # Bounding a2 based on Hasse-Weil lattice limits
        min_a2 = math.ceil(2 * sqrt_q * abs(a1)) - 2 * q
        max_a2 = math.floor((a1**2) / 4.0) + 2 * q
        
        for a2 in range(min_a2, max_a2 + 1):
            
            # 1. Serre's Point-Counting Defect Check
            # Number of rational points on the curve must be >= 0
            num_points_curve = q + 1 - a1
            if num_points_curve < 0:
                continue
                
            # 2. Decomposable Surface Filter
            # An abelian surface is decomposable if the Weil polynomial 
            # is the product of two elliptic curve polynomials.
            # Discriminant condition for splitting: Delta = a1^2 - 4a2 + 4q is a square 
            # and satisfies specific trace conditions.
            delta = a1**2 - 4 * a2 + 4 * q
            if delta >= 0 and ZZ(delta).is_square():
                # Further check if it splits into product of two elliptic curves
                # (Simplified check: if a1^2 - 4a2 + 4q is a square of an integer congruent to a1 mod 2)
                sqrt_delta = int(ZZ(delta).sqrt())
                if (a1 - sqrt_delta) % 2 == 0:
                    continue # Discard decomposable elliptic product

            # 3. Waterhouse p-adic Newton Polygon Constraints (Characteristic 2)
            # If a1 = 0, the 2-adic valuation restricts a2 odd/even pairings depending on extension k.
            if a1 == 0 and k % 2 != 0:
                # For odd extensions (e.g., F_8, k=3), if a1=0, a2 cannot be odd.
                if a2 % 2 != 0:
                    continue

            # 4. Calculate Theoretical Geometric Group Order N
            # N = P(1) = q^2 + 1 + a1(q + 1) + a2
            target_order = (q**2) + 1 + a1 * (q + 1) + a2
            
            # Insert valid isogeny target into curves table
            cursor.execute('''INSERT INTO curves (q, a1, a2, target_order)
                              VALUES (?, ?, ?, ?)''', (q, a1, a2, target_order))
            valid_count += 1
            
    conn.commit()
    conn.close()
    print(f"Successfully generated {valid_count} verified isogeny targets for q={q} (k={k}).")

# Example execution for F_64 (q=64)
if __name__ == "__main__":
    generate_isogeny_classes(64, db_path="verify_gf64_curves.db")
