import sqlite3
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import time
import scipy.stats.qmc as qmc
from sage.all import *

def worker_batch(chunk_indices, missing_dict):
    q_val = 64
    F = GF(q_val, 'z')
    R = PolynomialRing(F, 'x')
    F_elements = [F(0)] + [F('z')^i for i in range(q_val - 1)]
    
    results = []
    for indices in chunk_indices:
        h0, h1, h2, f0, f1, f2, f3, f4 = [F_elements[i] for i in indices]
        
        h = h2*R('x')**2 + h1*R('x') + h0
        f = R('x')**5 + f4*R('x')**4 + f3*R('x')**3 + f2*R('x')**2 + f1*R('x') + f0
        
        try:
            C = HyperellipticCurve(f, h)
            N1 = C.count_points(1)[0]
            N2 = C.count_points(2)[0]
            N = (N1**2 + N2) // 2
            isogeny_key = f"{N1}_{N}"
        except Exception:
            continue
            
        if isogeny_key in missing_dict:
            row_id = missing_dict[isogeny_key]
            
            # Compute invariants
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
                
            results.append((row_id, isogeny_key, str(h), str(f), str(invariants)))
            
    return results

if __name__ == '__main__':
    print(">>> SAGE SCRIPT INITIALIZING (ProcessPoolExecutor)...")
    db_name = "gf64_curves.db"
    num_workers = 4
    chunk_size = 4096
    
    if not os.path.exists(db_name):
        print(f"Error: {db_name} not found.")
        exit()
        
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS explicit_curves (
            id INTEGER PRIMARY KEY,
            h_poly TEXT,
            f_poly TEXT,
            invariant_factors TEXT,
            FOREIGN KEY(id) REFERENCES hyperelliptic_curves(id)
        )
    """)
    conn.commit()
    
    cursor.execute("""
        SELECT h.id, h.isogeny_class 
        FROM hyperelliptic_curves h
        LEFT JOIN explicit_curves e ON h.id = e.id
        WHERE e.id IS NULL AND h.isogeny_class IS NOT NULL
    """)
    missing_rows = cursor.fetchall()
    total_missing = len(missing_rows)
    
    if total_missing == 0:
        print("All explicit curves have already been found!")
        conn.close()
        exit()
        
    print(f"=== Multicore QMC Sieve for {db_name} ===")
    print(f"Loaded {total_missing} missing isogeny classes.")
    
    missing_dict = {row[1]: row[0] for row in missing_rows}
    sobol = qmc.Sobol(d=8, scramble=True)
    m_power = 15
    
    count = 0
    start_time = time.time()
    
    print(f"Igniting ProcessPoolExecutor with {num_workers} workers...")
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        try:
            while len(missing_dict) > 0:
                raw_samples = sobol.random_base2(m=m_power)
                int_indices = (raw_samples * 64).astype(int)
                
                # Submit tasks
                futures = []
                for i in range(0, len(int_indices), chunk_size):
                    chunk = int_indices[i:i + chunk_size]
                    futures.append(executor.submit(worker_batch, chunk, dict(missing_dict)))
                    
                # Collect results as they finish
                for future in as_completed(futures):
                    results = future.result()
                    if not results:
                        continue
                        
                    for row_id, iso_key, h_str, f_str, inv_str in results:
                        if iso_key in missing_dict:
                            cursor.execute("INSERT OR REPLACE INTO explicit_curves (id, h_poly, f_poly, invariant_factors) VALUES (?, ?, ?, ?)",
                                           (row_id, h_str, f_str, inv_str))
                            del missing_dict[iso_key]
                            count += 1
                            
                    conn.commit()
                    elapsed = time.time() - start_time
                    print(f"  -> Discovered {count} / {total_missing} missing explicit isomorphisms ({elapsed:.1f} sec)", end='\r', flush=True)
                    
                    if len(missing_dict) == 0:
                        break
                        
        except KeyboardInterrupt:
            print("\nShutting down executor...")
            
    conn.commit()
    conn.close()
    print("\n>>> Sieve execution completed.")
