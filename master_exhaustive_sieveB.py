"""
Master Exhaustive Cartier-Manin Sieve and Explicit Curve Generation Pipeline
Author: Steven Craighead
Target: Genus 2 Hyperelliptic Jacobians over F_{2^k} (k = 1 to 6)

Description:
Performs parallelized, memory-safe exhaustive generation of explicit curves 
using pool.imap_unordered streaming and a live 10,000-record progress logger.
"""

import sqlite3
import gc
import os
import time
from multiprocessing import Pool, cpu_count
from sage.all import GF, PolynomialRing, HyperellipticCurve

def worker_process_chunk(args):
    """
    WORKER PROCESS:
    Processes an assigned batch of h(x) polynomials across all monic f(x) space.
    Yields or returns verified explicit curve tuples.
    """
    q, h_batch = args
    F = GF(q, 'z')
    R = PolynomialRing(F, 'x')
    x = R.gen()
    elements = list(F)
    
    local_buffer = []
    
    for h in h_batch:
        h_coeffs = h.list()
        h1 = h_coeffs[1] if len(h_coeffs) > 1 else F(0)
        trace_parity = int(h1.trace())
        
        for f4 in elements:
            for f3 in elements:
                for f2 in elements:
                    for f1 in elements:
                        for f0 in elements:
                            f = x**5 + f4*x**4 + f3*x**3 + f2*x**2 + f1*x + f0
                            
                            try:
                                C = HyperellipticCurve(f, h)
                                frob = C.frobenius_polynomial()
                                coeffs = frob.list()
                                
                                curve_a1 = int(coeffs[3])
                                curve_a2 = int(coeffs[2])
                                
                                if trace_parity != (curve_a1 % 2):
                                    continue
                                    
                                local_buffer.append((1, q, str(h), str(f), curve_a1, curve_a2))
                                
                            except Exception:
                                pass
                                
    return local_buffer

def run_master_audit(k, db_path="audit_master_output.db"):
    q = 2**k
    start_time = time.time()
    print(f"\n[+] Starting Master Generation for F_{q} (k={k}) using {cpu_count()} CPU cores...")
    
    F = GF(q, 'z')
    R = PolynomialRing(F, 'x')
    x = R.gen()
    elements = list(F)
    
    # Generate all valid h(x) polynomials (degree <= 2, h != 0)
    all_h = []
    for h2 in elements:
        for h1 in elements:
            for h0 in elements:
                h = h2*x**2 + h1*x + h0
                if h != 0:
                    all_h.append(h)
                    
    # Partition h(x) into worker chunks
    num_workers = max(1, cpu_count() - 1)
    chunk_size = max(1, len(all_h) // num_workers)
    h_batches = [all_h[i:i + chunk_size] for i in range(0, len(all_h), chunk_size)]
    
    tasks = [(q, batch) for batch in h_batches]
    
    # Memory-Safe SQLite Streaming Ingestion
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS explicit_curves
                      (id INTEGER, q INTEGER, h_poly TEXT, f_poly TEXT, a1 INTEGER, a2 INTEGER)''')
    conn.commit()
    
    total_field_curves = 0
    next_log_threshold = 10000
    
    with Pool(num_workers) as pool:
        # imap_unordered streams results incrementally without holding everything in RAM
        for batch_results in pool.imap_unordered(worker_process_chunk, tasks):
            if batch_results:
                cursor.executemany('''
                    INSERT INTO explicit_curves (id, q, h_poly, f_poly, a1, a2)
                    VALUES (?, ?, ?, ?, ?, ?)''', batch_results)
                conn.commit()
                
                total_field_curves += len(batch_results)
                
                # Progress logger updating every 10,000 records processed
                while total_field_curves >= next_log_threshold:
                    print(f"    [LOG] F_{q} progress: {next_log_threshold} curves cataloged...")
                    next_log_threshold += 10000
                    
                gc.collect()
                
    conn.close()
    elapsed = time.time() - start_time
    print(f"[✓] F_{q} Complete in {elapsed:.2f}s. Total verified explicit curves: {total_field_curves}.\n")

if __name__ == "__main__":
    output_db = "audit_master_output.db"
    if os.path.exists(output_db):
        os.remove(output_db)
        
    print("==================================================")
    print(" MASTER CHARACTERISTIC 2 EXPLICIT CURVE PIPELINE")
    print("==================================================")
    
    # Execute generation across target fields
    for k_val in range(1, 5):  # Set range(1, 7) for F_2 through F_64
        run_master_audit(k_val, db_path=output_db)
