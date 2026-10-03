import sqlite3
import os
from sage.all import GF, PolynomialRing, HyperellipticCurve, lcm, factor

def fast_random_divisor(J, R, f, h):
    """
    Generates random Mumford representations natively in F_q[x] by picking v(x) 
    first and factoring v^2 + hv - f to find a valid u(x). 
    Zero field extensions. Zero coercion bugs. 
    """
    def get_one():
        fails = 0
        last_e = None
        while fails < 50:
            # 1. Guess a random polynomial v(x) of degree <= 2
            v_orig = R.random_element(degree=2)
            
            # 2. Compute the Mumford constraint polynomial (char 2, + is -)
            A = v_orig**2 + h*v_orig - f
            
            # 3. Factor natively in the base field F_q
            A_factors = A.factor()
            
            # 4. Extract a valid monic factor for u(x) of degree 1 or 2
            u = None
            
            # Prefer degree 2 to ensure we hit the general Jacobian manifold
            for P, multiplicity in A_factors:
                if P.degree() == 2:
                    u = P
                    break
                    
            # Fallback to degree 1 if no degree 2 factors exist
            if u is None:
                for P, multiplicity in A_factors:
                    if P.degree() == 1:
                        u = P
                        if multiplicity >= 2:
                            u = P**2  # Use a degree 2 divisor if the root is repeated
                        break
                        
            if u is None:
                continue # A(x) was an irreducible degree 5 polynomial, try again
                
            u = u.monic()
            
            # 5. Reduce v_orig modulo u
            v_red = v_orig % u
            
            try:
                return J([u, v_red])
            except Exception as e:
                fails += 1
                last_e = e
                continue
                
        raise RuntimeError(f"Sage rejected 50 mathematically valid divisors. Last error: {last_e}")
                
    # Summing two independent divisors ensures we cover the full group manifold
    return get_one() + get_one()


def patch_pending_invariants(db_path, q):
    if not os.path.exists(db_path):
        print(f"[!] Critical Error: File {db_path} does not exist in the current directory.")
        return

    F = GF(q, 'z')
    R = PolynomialRing(F, 'x')
    eval_vars = {'x': R.gen(), 'z': F.gen()} 
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT e.id, e.h_poly, e.f_poly, c.group_order 
            FROM explicit_curves e
            JOIN curves c ON e.id = c.id
            WHERE e.invariant_factors = 'PENDING'
        """)
        rows = cursor.fetchall()
        
    except sqlite3.OperationalError as e:
        print(f"[!] SQLite Error reading {db_path}: {e}")
        conn.close()
        return
    
    if not rows:
        print(f"No PENDING invariants found in {db_path}.")
        conn.close()
        return

    print(f"Patching {len(rows)} curves in {db_path}...")
    
    update_buffer = []
    
    for row in rows:
        curve_id, h_str, f_str, target_order = row
        
        h_poly = R(eval(h_str.replace('^', '**'), eval_vars))
        f_poly = R(eval(f_str.replace('^', '**'), eval_vars))
        
        C = HyperellipticCurve(f_poly, h_poly)
        J = C.jacobian()
        
        L_poly = C.zeta_function().numerator()
        geometric_order = L_poly(1)
        
        if geometric_order != target_order:
            print(f"[!] Warning: Zeta order {geometric_order} != Target {target_order} for ID {curve_id}")
            continue
            
        group_exponent = 1
        max_samples = 30  
        
        for _ in range(max_samples):
            # USING THE PURE F_q ALGEBRAIC BYPASS
            D = fast_random_divisor(J, R, f_poly, h_poly)
            
            factors = factor(geometric_order)
            D_order = geometric_order
            
            for p, _ in factors:
                while D_order % p == 0:
                    if (D_order // p) * D == J(0):
                        D_order //= p
                    else:
                        break
                        
            group_exponent = lcm(group_exponent, D_order)
            if geometric_order % group_exponent != 0:
                continue 

        invariant_factors = []
        remaining_order = geometric_order
        
        while remaining_order > 1:
            invariant_factors.append(int(group_exponent))
            remaining_order //= group_exponent
            
        invariant_factors.reverse() 
        
        update_buffer.append((str(invariant_factors), curve_id))
        
        if len(update_buffer) >= 50:
            cursor.executemany("""
                UPDATE explicit_curves 
                SET invariant_factors = ? 
                WHERE id = ?
            """, update_buffer)
            conn.commit()
            update_buffer = []

    if update_buffer:
        cursor.executemany("""
            UPDATE explicit_curves 
            SET invariant_factors = ? 
            WHERE id = ?
        """, update_buffer)
        conn.commit()

    conn.close()
    print(f"Database {db_path} structural patching complete.")


databases = [
    (2, 'gf2_curves.db'),
    (4, 'gf4_curves.db'),
    (8, 'gf8_curves.db'),
    (16, 'gf16_curves.db'),
    (32, 'gf32_curves.db'),
    (64, 'gf64_curves.db')
]

for q, db_path in databases:
    patch_pending_invariants(db_path, q)
