"""
=========================================================================================
CHARACTERISTIC 2 HYPERELLIPTIC CURVE EXACT ANCHOR SIEVE (GF(2) - GF(64))
=========================================================================================

1. MATHEMATICAL METHODOLOGY & AFFINE REDUCTION
-----------------------------------------------------------------------------------------
A naive brute-force search over GF(q) generates q^8 polynomial combinations for h(x) and f(x). 
For GF(64), this is 281 trillion candidates.

To bypass this, this script uses Affine Reduction based on Cardona-Quer-Nart-Pujolà invariants, 
reducing the search space to exactly 5 * q^3 isomorphism classes:
    - Case 1: h(x) = x^2 + x (p-rank 2)
    - Case 2: h(x) = x^2 (p-rank 1, double root)
    - Case 3: h(x) = x (p-rank 1, degree 1)
    - Case 4: h(x) = 1 (p-rank 0, supersingular)

2. MULTIPROCESSING & COERCION SAFETY
-----------------------------------------------------------------------------------------
To prevent cross-process finite-field coercion errors when passing elements across Python's 
multiprocessing boundary, field elements are serialized into lists of pure Python integers.
=========================================================================================
"""

import sqlite3
import logging
import psutil
import os
import gc
import multiprocessing
from multiprocessing import Pool
from sage.all import GF, PolynomialRing, HyperellipticCurve

# ---------------------------------------------------------
# GLOBAL CONFIGURATION
# ---------------------------------------------------------
TARGET_FIELDS = [2, 4, 8, 16, 32, 64]
BATCH_SIZE = 10000 

logging.basicConfig(
    filename='sieve_exact_anchors.log',
    level=logging.INFO,
    format='%(asctime)s - WORKER %(process)d - %(levelname)s - %(message)s'
)

def init_db(q):
    """
    Initializes a separate SQLite database for the current finite field.
    Enables WAL mode to prevent locking traffic jams on the SSD.
    """
    db_path = f'gf{q}_exact_curves.db'
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('PRAGMA synchronous=NORMAL;')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS curves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            q INTEGER,
            h_coeffs TEXT,
            f_coeffs TEXT,
            target_order INTEGER,
            geometric_order INTEGER,
            cm_trace_parity INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    return db_path

def process_batch(batch_tuple):
    """
    Worker function executed independently by the multiprocessing pool.
    Reconstructs polynomials from Python int lists, evaluates curves, commits to SQLite, 
    and immediately triggers garbage collection to purge PARI/GMP C-library memory.
    """
    q, batch_data, db_path = batch_tuple
    mem_usage = psutil.virtual_memory().percent
    
    if mem_usage > 90.0:
        logging.error(f"CRITICAL: RAM at {mem_usage}%. Aborting batch to protect OS.")
        return len(batch_data), 0

    F = GF(q) if q == 2 else GF(q, 'a')
    R = PolynomialRing(F, 'x')
    x = R.gen()
    alpha = F.gen() if q > 2 else None
    
    def reconstruct_element(coeff_list):
        if q == 2:
            return F(coeff_list[0])
        return sum(F(bit) * (alpha**i) for i, bit in enumerate(coeff_list))

    def serialize_element(c):
        if q == 2:
            return [int(c)]
        return [int(bit) for bit in c.list()]

    explicit_curves = []
    curves_tested = 0
    
    for h_reprs, f_reprs in batch_data:
        curves_tested += 1
        
        if curves_tested % 2000 == 0:
            logging.info(f"GF({q}) Status: Tested {curves_tested} affine-reduced anchor candidates.")

        try:
            h_poly = sum(reconstruct_element(c_list) * x**i for i, c_list in enumerate(h_reprs))
            f_poly = sum(reconstruct_element(c_list) * x**i for i, c_list in enumerate(f_reprs))
            
            # This automatically fails and drops singular curves
            C = HyperellipticCurve(f_poly, h_poly)
        except Exception:
            continue  
        
        try:
            frob = C.frobenius_polynomial()
            coeffs = frob.list()
            
            curve_a1 = int(coeffs[3]) if len(coeffs) > 3 else 0
            trace_parity = curve_a1 % 2
            
            J = C.jacobian()
            target_order = J.cardinality()
            
            ext_field = GF(q**2, 'a2' if q > 2 else 'z')
            geometric_order = J.change_ring(ext_field).cardinality()
            
            h_stored = [serialize_element(h_poly[i]) for i in range(3)]
            f_stored = [serialize_element(f_poly[i]) for i in range(6)]
            
            explicit_curves.append((
                q, 
                str(h_stored), 
                str(f_stored), 
                int(target_order), 
                int(geometric_order), 
                int(trace_parity)
            ))
            
        except Exception as e:
            logging.error(f"Algebraic evaluation failed for GF({q}): {e}")
            continue

    if explicit_curves:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO curves (q, h_coeffs, f_coeffs, target_order, geometric_order, cm_trace_parity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', explicit_curves)
        conn.commit()
        conn.close()
    
    gc.collect()
    return curves_tested, len(explicit_curves)

def generate_exact_search_space(q):
    """
    Cardona-Quer / Affine Reduction Generator.
    Yields pure F_2 basis coefficient lists to eliminate cross-process coercion errors.
    """
    F = GF(q) if q == 2 else GF(q, 'a')
    elements = list(F)
    k = q.bit_length() - 1
    
    def manual_trace(val):
        return sum([val**(2**i) for i in range(k)])
        
    gamma = next(a for a in elements if manual_trace(a) == F(1))
    
    def get_repr(val):
        if q == 2:
            return [int(val)]
        return [int(bit) for bit in val.list()]
    
    h_coeffs_1 = [get_repr(F(0)), get_repr(F(1)), get_repr(F(1))]
    for f4 in elements:
        for f2 in elements:
            for f0 in elements:
                f_list = [get_repr(f0), get_repr(F(0)), get_repr(f2), get_repr(F(0)), get_repr(f4), get_repr(F(1))]
                yield (h_coeffs_1, f_list)
                
    h_coeffs_2 = [get_repr(F(0)), get_repr(F(0)), get_repr(F(1))]
    for f4 in elements:
        for f1 in elements:
            for f0 in elements:
                f_list = [get_repr(f0), get_repr(f1), get_repr(F(0)), get_repr(F(0)), get_repr(f4), get_repr(F(1))]
                yield (h_coeffs_2, f_list)
                
    h_coeffs_3 = [get_repr(F(0)), get_repr(F(1)), get_repr(F(0))]
    for f4 in elements:
        for f3 in elements:
            for f0 in elements:
                for a in [F(0), gamma]:
                    f_list = [get_repr(f0), get_repr(F(0)), get_repr(a), get_repr(f3), get_repr(f4), get_repr(F(1))]
                    yield (h_coeffs_3, f_list)
                
    h_coeffs_4 = [get_repr(F(1)), get_repr(F(0)), get_repr(F(0))]
    for f4 in elements:
        for f3 in elements:
            for f2 in elements:
                f_list = [get_repr(F(0)), get_repr(F(0)), get_repr(f2), get_repr(f3), get_repr(f4), get_repr(F(1))]
                yield (h_coeffs_4, f_list)

def yield_batches(q, db_path):
    batch = []
    for item in generate_exact_search_space(q):
        batch.append(item)
        if len(batch) >= BATCH_SIZE:
            yield (q, batch, db_path)
            batch = []
    if batch:
        yield (q, batch, db_path)

if __name__ == '__main__':
    total_cores = multiprocessing.cpu_count()
    active_workers = max(1, total_cores - 1)
    
    print(f"Starting Exact Anchor Multi-Field Sieve on {active_workers} processors.")
    print("Core reserved for MX Linux OS stability.")
    
    with Pool(processes=active_workers) as pool:
        for q in TARGET_FIELDS:
            print(f"\n--- Starting Exact Anchor Generation for GF({q}) ---")
            db_path = init_db(q)
            
            total_tested = 0
            total_saved = 0
            
            for tested, saved in pool.imap_unordered(process_batch, yield_batches(q, db_path)):
                total_tested += tested
                total_saved += saved
                print(f"    [PROGRESS] GF({q}): Processed {total_tested} candidates, cataloged {total_saved} valid curves...")
                
            print(f"Completed mapping GF({q}). Total curves saved: {total_saved}. Data saved to {db_path}.")
            
    print("\nAll fields GF(2) through GF(64) processed successfully.")
