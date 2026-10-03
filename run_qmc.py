import sqlite3
import os
import time
import scipy.stats.qmc as qmc

db_name = "gf64_curves.db"
q_val = 64

print(f"\n=== Initializing Corrected QMC Sieve for {db_name} ===")

if not os.path.exists(db_name):
    print(f"Error: {db_name} not found in this directory.")
else:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS explicit_curves (
            id INTEGER PRIMARY KEY,
            h_poly TEXT,
            f_poly TEXT,
            invariant_factors TEXT,
            FOREIGN KEY(id) REFERENCES curves(id)
        )
    """)
    conn.commit()
    
    cursor.execute("""
        SELECT c.id, c.group_order 
        FROM curves c
        LEFT JOIN explicit_curves e ON c.id = e.id
        WHERE e.id IS NULL AND c.group_order IS NOT NULL
    """)
    missing_rows = cursor.fetchall()
    
    total_missing = len(missing_rows)
    
    if total_missing == 0:
        print("All explicit curves have already been found!")
        conn.close()
    else:
        print(f"Loaded {total_missing} missing Jacobian group order targets.")
        
        missing_dict = {str(row[1]).strip(): row[0] for row in missing_rows}
        
        F = GF(q_val, 'z')
        R = PolynomialRing(F, 'x')
        F_elements = [F(0)] + [F('z') ** i for i in range(q_val - 1)]
        
        sobol = qmc.Sobol(d=8, scramble=True)
        block_size = 1024  
        
        count = 0
        tested_count = 0
        start_time = time.time()
        
        print("Igniting Sobol sequence generator with correct Jacobian order calculation...")
        
        try:
            while len(missing_dict) > 0:
                raw_samples = sobol.random(n=block_size)
                int_indices = (raw_samples * 64).astype(int)
                
                for indices in int_indices:
                    if len(missing_dict) == 0:
                        break
                        
                    tested_count += 1
                    h0, h1, h2, f0, f1, f2, f3, f4 = [F_elements[i] for i in indices]
                    
                    h = h2 * R('x')**2 + h1 * R('x') + h0
                    f = R('x')**5 + f4 * R('x')**4 + f3 * R('x')**3 + f2 * R('x')**2 + f1 * R('x') + f0
                    
                    try:
                        C = HyperellipticCurve(f, h)
                        # Extract curve point counts over F_q and F_{q^2}
                        N1 = int(C.count_points(1)[0])
                        N2 = int(C.count_points(2)[0])
                        
                        # Reconstruct Weil coefficients (a1, a2) and exact Jacobian group order N
                        a1 = q_val + 1 - N1
                        a2 = (N2 - q_val**2 - 1 + a1**2) // 2
                        N = 1 + (q_val + 1) * a1 + a2 + q_val**2
                        group_str = str(N)
                    except Exception:
                        continue
                        
                    if group_str in missing_dict:
                        row_id = missing_dict.pop(group_str)
                        
                        J = C.jacobian()
                        prime_factors = list(factor(N))
                        max_p_orders = {p: 0 for p, _ in prime_factors}
                        
                        for _ in range(40):
                            try:
                                D = J.random_element()
                            except Exception:
                                continue
                                
                            for p, v in prime_factors:
                                if max_p_orders[p] == v: continue  
                                cofactor = N // (p**v)
                                Dp = cofactor * D
                                p_ord = 0
                                while Dp != J(0) and p_ord <= v:
                                    Dp = p * Dp
                                    p_ord += 1
                                if p_ord > max_p_orders[p]: max_p_orders[p] = p_ord
                                    
                        p_partitions = {}
                        for p, v in prime_factors:
                            e = max_p_orders[p]
                            if e == v: p_partitions[p] = [e]
                            elif e == v - 1: p_partitions[p] = [e, 1]
                            else: p_partitions[p] = [e, v - e]
                                
                        max_rank = max((len(part) for part in p_partitions.values()), default=0)
                        if max_rank == 0: invariants = [N]
                        else:
                            invariants = [1] * max_rank
                            for p, part in p_partitions.items():
                                for i, exp in enumerate(part): invariants[i] *= (int(p)**exp)
                            invariants = sorted([inv for inv in invariants if inv > 1])
                        
                        cursor.execute("INSERT OR REPLACE INTO explicit_curves (id, h_poly, f_poly, invariant_factors) VALUES (?, ?, ?, ?)",
                                       (row_id, str(h), str(f), str(invariants)))
                        count += 1
                        conn.commit()
                        print(f"\n  >>> MATCH FOUND! Discovered {count} / {total_missing} (Jacobian Order: {N})")
                        
                    if tested_count % 100 == 0:
                        elapsed = time.time() - start_time
                        print(f"  [Tested: {tested_count} | Found: {count}/{total_missing}] Elapsed: {elapsed:.1f}s", end='\r', flush=True)
                        
        except KeyboardInterrupt:
            print("\n\nExecution paused by user. Saving progress...")
            
        conn.commit()
        conn.close()
        print(f"\n>>> Sieve batch completed. Total found: {count}")
