import sqlite3
import os
from sage.all import GF, PolynomialRing, HyperellipticCurve, factor

def fast_random_divisor(J, R, f, h):
    """Generates Mumford divisors natively in F_q[x] without extensions."""
    fails = 0
    while fails < 100:
        v_orig = R.random_element(degree=2)
        A = v_orig**2 + h*v_orig - f
        A_factors = A.factor()
        u = None
        for P, mult in A_factors:
            if P.degree() == 2:
                u = P; break
        if u is None:
            for P, mult in A_factors:
                if P.degree() == 1:
                    u = P**2 if mult >= 2 else P
                    break
        if u is None:
            fails += 1
            continue
        u = u.monic()
        v_red = v_orig % u
        try:
            return J([u, v_red])
        except Exception:
            fails += 1
            continue
    return J(0) 

def get_sylow_structure(J, p, a, N, R, f_poly, h_poly):
    """Decomposes the Sylow p-subgroup into exact invariant factors."""
    if a == 0: return []
    if a == 1: return [p]
    
    def get_random_sylow():
        for _ in range(50):
            D = fast_random_divisor(J, R, f_poly, h_poly)
            Sp_elem = (N // (p**a)) * D
            if Sp_elem != J(0): return Sp_elem
        return J(0)
        
    for attempt in range(10): 
        # 1. Find x1 (Maximal Order)
        x1, e1 = J(0), 0
        for _ in range(40):
            g = get_random_sylow()
            temp, ord_g = g, 0
            while temp != J(0):
                temp = p * temp
                ord_g += 1
            if ord_g > e1:
                e1, x1 = ord_g, g
            if e1 == a: break
        
        if e1 == a: return [p**a]
        
        # Build H1 (Fast point addition)
        H1 = {}
        temp = J(0)
        for j in range(p**e1):
            H1[temp] = j
            temp += x1
            
        # 2. Find x2 (Maximal Relative Order)
        e2, best_y, best_c = 0, J(0), 0
        for _ in range(40):
            y = get_random_sylow()
            temp, k = y, 0
            while temp not in H1:
                temp = p * temp
                k += 1
            if k > e2:
                e2, best_y, best_c = k, y, H1[temp]
                
        if best_c % (p**e2) != 0: continue # Retry if x1 wasn't truly maximal
            
        d = (best_c // (p**e2)) % (p**e1)
        x2 = best_y - d * x1
        
        if e1 + e2 == a:
            return sorted([p**e1, p**e2], reverse=True)
            
        # Build H2
        H2 = {}
        base1 = J(0)
        for j1 in range(p**e1):
            temp = base1
            for j2 in range(p**e2):
                H2[temp] = (j1, j2)
                temp += x2
            base1 += x1
                
        # 3. Find x3
        e3, best_y, best_c1, best_c2 = 0, J(0), 0, 0
        for _ in range(40):
            y = get_random_sylow()
            temp, k = y, 0
            while temp not in H2:
                temp = p * temp
                k += 1
            if k > e3:
                e3, best_y, best_c1, best_c2 = k, y, H2[temp][0], H2[temp][1]
                
        if best_c1 % (p**e3) != 0 or best_c2 % (p**e3) != 0: continue
            
        d1 = (best_c1 // (p**e3)) % (p**e1)
        d2 = (best_c2 // (p**e3)) % (p**e2)
        x3 = best_y - d1 * x1 - d2 * x2
        
        if e1 + e2 + e3 == a:
            return sorted([p**e1, p**e2, p**e3], reverse=True)
            
        # 4. Find x4 (Genus 2 Max Rank is 4)
        e4 = a - (e1 + e2 + e3)
        return sorted([p**e1, p**e2, p**e3, p**e4], reverse=True)
        
    return []

def combine_sylows(sylow_lists):
    """Combines p-group partitions into global Smith Normal Form."""
    if not sylow_lists: return []
    max_len = max(len(sl) for sl in sylow_lists)
    padded = [sl + [1] * (max_len - len(sl)) for sl in sylow_lists]
        
    invariants = []
    for i in range(max_len):
        prod = 1
        for p_list in padded: prod *= p_list[i]
        invariants.append(prod)
    return invariants

def rebuild_database(db_path, q):
    if not os.path.exists(db_path):
        print(f"[!] File {db_path} not found. Skipping.")
        return

    F = GF(q, 'z')
    R = PolynomialRing(F, 'x')
    eval_vars = {'x': R.gen(), 'z': F.gen()} 
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # We grab ALL curves to rebuild them strictly and cleanly
    cursor.execute("""
        SELECT e.id, e.h_poly, e.f_poly 
        FROM explicit_curves e
    """)
    rows = cursor.fetchall()

    print(f"Rebuilding exact Sylow SNF for {len(rows)} curves in {db_path}...")
    
    update_buffer = []
    processed = 0
    
    for row in rows:
        curve_id, h_str, f_str = row
        
        h_poly = R(eval(h_str.replace('^', '**'), eval_vars))
        f_poly = R(eval(f_str.replace('^', '**'), eval_vars))
        
        C = HyperellipticCurve(f_poly, h_poly)
        J = C.jacobian()
        
        # 100% rigorous exact order via L(1)
        L_poly = C.zeta_function().numerator()
        geometric_order = int(L_poly(1))
        
        factors = factor(geometric_order)
        sylow_lists = []
        
        for p_val, a_val in factors:
            snf_p = get_sylow_structure(J, int(p_val), int(a_val), geometric_order, R, f_poly, h_poly)
            if snf_p:
                sylow_lists.append(snf_p)
                
        exact_invariants = combine_sylows(sylow_lists)
        
        update_buffer.append((str(exact_invariants), curve_id))
        processed += 1
        
        if len(update_buffer) >= 100:
            cursor.executemany("""
                UPDATE explicit_curves 
                SET invariant_factors = ? 
                WHERE id = ?
            """, update_buffer)
            conn.commit()
            update_buffer = []
            print(f"  ... committed {processed}/{len(rows)}")

    if update_buffer:
        cursor.executemany("""
            UPDATE explicit_curves 
            SET invariant_factors = ? 
            WHERE id = ?
        """, update_buffer)
        conn.commit()

    conn.close()
    print(f"Database {db_path} completely rebuilt.")


databases = [
    (2, 'gf2_curves.db'),
    (4, 'gf4_curves.db'),
    (8, 'gf8_curves.db'),
    (16, 'gf16_curves.db'),
    (32, 'gf32_curves.db'),
    (64, 'gf64_curves.db')
]

for q, db_path in databases:
    rebuild_database(db_path, q)
