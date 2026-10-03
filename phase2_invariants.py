import sqlite3
import os
import time

def process_database(db_name, q_val):
    print(f"\n--- Locating {db_name} ---")
    if not os.path.exists(db_name):
        print(f"  -> ERROR: {db_name} not found in {os.getcwd()}")
        return
        
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT id, h_poly, f_poly, jacobian_points FROM hyperelliptic_curves WHERE invariant_factors IS NULL")
    rows = cursor.fetchall()
    
    total_rows = len(rows)
    if total_rows == 0:
        print(f"  -> All invariants for {db_name} are already built. Skipping.")
        conn.close()
        return
        
    print(f"=== Phase 2: {db_name} (q={q_val}) ===")
    print(f"Processing {total_rows} curves...")
    
    # Sage will automatically know what GF and PolynomialRing mean here
    F = GF(q_val, 'z')
    R = PolynomialRing(F, 'x')
    
    start_time = time.time()
    count = 0
    
    for row in rows:
        row_id, h_str, f_str, N = row
        
        try:
            h = R(h_str)
            f = R(f_str)
            C = HyperellipticCurve(f, h)
            J = C.jacobian()
            
            prime_factors = list(factor(N))
            max_p_orders = {p: 0 for p, _ in prime_factors}
            
            # Autonomous Divisor Sampling Algorithm
            for _ in range(40):
                try:
                    D = J.random_element()
                except Exception:
                    continue
                    
                for p, v in prime_factors:
                    if max_p_orders[p] == v:
                        continue  
                        
                    cofactor = N // (p**v)
                    Dp = cofactor * D
                    
                    p_ord = 0
                    while Dp != J(0) and p_ord <= v:
                        Dp = p * Dp
                        p_ord += 1
                        
                    if p_ord > max_p_orders[p]:
                        max_p_orders[p] = p_ord
                        
            # Determine structural partitions
            p_partitions = {}
            for p, v in prime_factors:
                e = max_p_orders[p]
                if e == v:
                    p_partitions[p] = [e]
                elif e == v - 1:
                    p_partitions[p] = [e, 1]
                else:
                    p_partitions[p] = [e, v - e]
                    
            # Assemble properly merged Smith Normal Form invariants
            max_rank = max((len(part) for part in p_partitions.values()), default=0)
            if max_rank == 0:
                invariants = [N]
            else:
                invariants = [1] * max_rank
                for p, part in p_partitions.items():
                    for i, exp in enumerate(part):
                        invariants[i] *= (int(p)**exp)
                        
                invariants = sorted([inv for inv in invariants if inv > 1])
                
            snf_str = str(invariants)
            
        except Exception:
            snf_str = str([N])
            
        cursor.execute("UPDATE hyperelliptic_curves SET invariant_factors=? WHERE id=?", (snf_str, row_id))
        count += 1
        
        if count % 250 == 0 or count == total_rows:
            conn.commit()
            rate = count / (time.time() - start_time)
            print(f"  -> Built {count}/{total_rows} invariants ({rate:.1f} curves/sec)", end='\r', flush=True)
            
    conn.commit()
    conn.close()
    print(f"\n[{db_name}] >>> Successfully mapped {count} abelian group structures!")

databases = {
    "Unique_GF32.db": 32,
    "Unique_GF16.db": 16,
    "Unique_GF8.db": 8,
    "Unique_GF4.db": 4,
    "Unique_GF2.db": 2
}

print("\n>>> SCRIPT LOADED. EXECUTING Phase 2...")
for db, q in databases.items():
    process_database(db, q)
    
print("\n>>> ALL TASKS COMPLETE.")
