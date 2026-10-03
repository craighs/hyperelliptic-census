"""
Master Exhaustive Cartier-Manin Sieve and Explicit Curve Generation Pipeline
Author: Steven Craighead
Target: Genus 2 Hyperelliptic Jacobians over F_{2^k} (k = 1 to 6)

Description:
This production script performs an exhaustive, parallelized audit and generation 
of explicit hyperelliptic curves (h(x), f(x)) and their corresponding Frobenius 
invariants (a1, a2) across finite fields of characteristic 2. It incorporates 
a lossless Cartier-Manin trace parity filter and writes safely to an isolated 
audit database to prevent any unintended modification of production master files.
"""

import sqlite3
import gc
import os
from multiprocessing import Pool, cpu_count
from sage.all import GF, PolynomialRing, HyperellipticCurve

def worker_process_chunk(q, h_batch):
    """
    STAGE 3 & 4 WORKER: 
    Processes a specific batch of h(x) polynomials across all monic f(x) space.
    Returns a list of verified explicit curve tuples for safe central ingestion.
    """
    F = GF(q, 'z')
    R = PolynomialRing(F, 'x')
    x = R.gen()
    elements = list(F)
    
    local_buffer = []
    
    for h in h_batch:
        # Extract linear coefficient h1 for Cartier-Manin trace parity filtering
        # In Sage, h can be parsed or evaluated. Since h is built as a polynomial,
        # we extract its coefficients directly.
        h_coeffs = h.list()
        h1 = h_coeffs[1] if len(h_coeffs) > 1 else F(0)
        
        # Lossless Cartier-Manin trace parity condition: Tr(M) mod 2 == a1 mod 2
        # We store the parity integer to filter during inner-loop invariant extraction.
        trace_parity = int(h1.trace())
        
        for f4 in elements:
            for f3 in elements:
                for f2 in elements:
                    for f1 in elements:
                        for f0 in elements:
                            f = x**5 + f4*x**4 + f3*x**3 + f2*x**2 + f1*x + f0
                            
                            try:
                                # STAGE 5: Geometric Smoothness & Point-Counting Verification
                                # Sage's HyperellipticCurve constructor natively validates 
                                # non-singular geometry in characteristic 2.
                                C = HyperellipticCurve(f, h)
                                frob = C.frobenius_polynomial()
                                coeffs = frob.list()
                                
                                curve_a1 = int(coeffs[3])
                                curve_a2 = int(coeffs[2])
                                
                                # Verify Cartier-Manin trace parity alignment
                                if trace_parity != (curve_a1 % 2):
                                    continue
                                    
                                local_buffer.append((1, q, str(h), str(f), curve_a1, curve_a2))
                                
                            except Exception:
                                # Discard singular or malformed curve instances silently
                                pass
                                
    return local_buffer

def run_master_audit(k, db_path="audit_master_output.db"):
    """
    STAGE 1 & 2: Initialization and Workload Partitioning.
    Sets up the finite field F_{2^k}, partitions the h(x) search space into 
    parallel chunks, and dispatches them across available CPU cores.
    """
    q = 2**k
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
                    
    # Partition h(x) polynomials into chunks for multiprocessing
    num_workers = max(1, cpu_count() - 1)
    chunk_size = max(1, len(all_h) // num_workers)
    h_batches = [all_h[i:i + chunk_size] for i in range(0, len(all_h), chunk_size)]
    
    # Prepare argument tuples for worker pool
    tasks = [(q, batch) for batch in h_batches]
    
    # STAGE 6: Centralized Database Ingestion and Transaction Management
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS explicit_curves
                      (id INTEGER, q INTEGER, h_poly TEXT, f_poly TEXT, a1 INTEGER, a2 INTEGER)''')
    conn.commit()
    
    total_field_curves = 0
    
    with Pool(num_workers) as pool:
        for batch_results in pool.starmap(worker_process_chunk, tasks):
            if batch_results:
                cursor.executemany('''
                    INSERT INTO explicit_curves (id, q, h_poly, f_poly, a1, a2)
                    VALUES (?, ?, ?, ?, ?, ?)''', batch_results)
                conn.commit()
                total_field_curves += len(batch_results)
                
    conn.close()
    print(f"[✓] F_{q} Complete. Cataloged {total_field_curves} verified explicit curves into {db_path}.\n")

if __name__ == "__main__":
    # Isolate output database to ensure zero risk to existing production master files
    output_db = "audit_master_output.db"
    if os.path.exists(output_db):
        os.remove(output_db)
        
    print("==================================================")
    print(" MASTER CHARACTERISTIC 2 EXPLICIT CURVE PIPELINE")
    print("==================================================")
    
    # Execute generation across all target field extensions F_2 through F_64 (k=1 to 6)
    for k_val in range(1, 7):
        run_master_audit(k_val, db_path=output_db)
        
    print("All field audits successfully completed. Compare results against gf_master.db using audit_content.py.")
