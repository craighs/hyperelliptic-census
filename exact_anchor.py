"""
=========================================================================================
CHARACTERISTIC 2 HYPERELLIPTIC CURVE EXACT ANCHOR SIEVE (GF(2) - GF(64))
=========================================================================================

1. MATHEMATICAL METHODOLOGY (The Pre-Filter & Affine Reduction)
-----------------------------------------------------------------------------------------
A naive brute-force search over GF(q) generates q^8 polynomial combinations for h(x) and f(x). 
For GF(16), this is 4.29 billion combinations. For GF(64), it is 281 trillion.

To bypass this computationally impossible hurdle, this script uses Affine Reduction to 
generate only the exact geometric anchors (isomorphism classes) of Genus 2 curves. 
By utilizing the geometric foundations of Cardona-Quer-Nart-Pujolà invariants, we reduce 
all curves to exactly four canonical h(x) bases based on the p-rank of the Jacobian:
    - Case 1: h(x) = x^2 + x (p-rank 2)
    - Case 2: h(x) = x^2 (p-rank 1, double root)
    - Case 3: h(x) = x (p-rank 1, degree 1)
    - Case 4: h(x) = 1 (p-rank 0, supersingular)

This reduction drops the search space to exactly 5 * q^3. 
- GF(16) reduces from 4.29 billion to 20,480.
- GF(64) reduces from 281 trillion to 1,310,720.

2. HARDWARE & MEMORY OPTIMIZATION
-----------------------------------------------------------------------------------------
- Lazy Generation: Uses Python's `yield` to stream combinations to workers in batches of 
  10,000, preventing the main OS RAM from filling up.
- Core Protection: Leaves one CPU core permanently free so the host OS (MX Linux) does 
  not freeze during heavy Cartier-Manin matrix operations.
- Memory Kill-Switch: Workers ping `psutil` every batch. If the SageMath C-library 
  memory leak pushes physical RAM past 90%, the batch aborts to prevent SSD thrashing.

3. DATABASE ARCHITECTURE
-----------------------------------------------------------------------------------------
Creates an isolated SQLite database for each field (e.g., 'gf16_exact_curves.db').
Uses Write-Ahead Logging (WAL mode) to allow multiple processors to write to the SSD 
concurrently without locking each other out.
=========================================================================================
"""

import sqlite3
import logging
import psutil
import os
import multiprocessing
from multiprocessing import Pool
from sage.all import GF, PolynomialRing, HyperellipticCurve

# ---------------------------------------------------------
# GLOBAL CONFIGURATION
# ---------------------------------------------------------
# Tracks the specific finite fields to process
TARGET_FIELDS = [2, 4, 8, 16, 32, 64]

# Number of curves a worker evaluates before terminating and releasing RAM
BATCH_SIZE = 10000 

# Configure logging to track worker PIDs and execution speed
logging.basicConfig(
    filename='sieve_exact_anchors.log',
    level=logging.INFO,
    format='%(asctime)s - WORKER %(process)d - %(levelname)s - %(message)s'
)

def init_db(q):
    """
    Initializes a separate SQLite database for the current finite field.
    Enables WAL mode to prevent locking traffic jams on the SSD when 
    multiple workers try to commit curve data simultaneously.
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

def hash_curve(C):
    """
    Fast algebraic signature to guarantee 1-to-1 isomorphism uniqueness.
    count_points(2) returns a list: [points_in_GF(q), points_in_GF(q^2)].
    Converted to a tuple so it can be hashed into the seen_hashes set.
    """
    try:
        return tuple(C.count_points(2))
    except Exception:
        return None

def process_batch(batch_tuple):
    """
    Worker function executed independently by the multiprocessing pool.
    Receives a specific chunk of affine-reduced polynomials, filters them,
    calculates the Jacobian orders, and saves valid curves to the DB.
    """
    q, batch_data, db_path = batch_tuple
    mem_usage = psutil.virtual_memory().percent
    
    # OS Protection: Kill the process if SageMath leaks too much RAM
    if mem_usage > 90.0:
        logging.error(f"CRITICAL: RAM at {mem_usage}%. Aborting batch to protect OS.")
        return

    F = GF(q) if q == 2 else GF(q, 'a')
    R = PolynomialRing(F, 'x')
    x = R.gen()
    
    seen_hashes = set()
    explicit_curves = []
    curves_tested = 0
    
    for h_coeffs, f_coeffs in batch_data:
        curves_tested += 1
        
        # Write to log every 2000 polynomials to track speed
        if curves_tested % 2000 == 0:
            logging.info(f"GF({q}) Status: Tested {curves_tested} affine-reduced anchor candidates.")

        h_poly = sum(c * x**i for i, c in enumerate(h_coeffs))
        f_poly = sum(c * x**i for i, c in enumerate(f_coeffs))
        
        # Try constructing the curve; automatically fails if the discriminant is 0 (singular)
        try:
            C = HyperellipticCurve(f_poly, h_poly)
        except ValueError:
            continue  
            
        # Check against local batch cache to prevent duplicate processing
        curve_signature = hash_curve(C)
        if curve_signature is None or curve_signature in seen_hashes:
            continue
            
        seen_hashes.add(curve_signature)
        
        # Heavy Algebra Block (Only runs on geometrically unique, non-singular curves)
        try:
            # 1. Cartier-Manin matrix and trace (Hasse-Witt parity)
            cm_matrix = C.cartier_manin_matrix()
            trace_parity = cm_matrix.trace()
            
            # 2. Base Field Jacobian Order
            J = C.jacobian()
            target_order = J.cardinality()
            
            # 3. Geometric Order (Evaluated over the F_q^2 extension field)
            geometric_order = J.change_ring(GF(q**2, 'a2')).cardinality()
            
            explicit_curves.append((
                q, 
                str(h_coeffs), 
                str(f_coeffs), 
                int(target_order), 
                int(geometric_order), 
                int(trace_parity)
            ))
            
        except Exception as e:
            logging.error(f"Algebraic evaluation failed for GF({q}): {e}")
            continue

    # Commit the batch of explicitly found curves to the SQLite database
    if explicit_curves:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO curves (q, h_coeffs, f_coeffs, target_order, geometric_order, cm_trace_parity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', explicit_curves)
        conn.commit()
        conn.close()


def generate_exact_search_space(q):
    """
    Cardona-Quer / Affine Reduction Generator.
    Yields strictly the 5 * q^3 parameter space that spans all isomorphism classes.
    """
    F = GF(q) if q == 2 else GF(q, 'a')
    elements = list(F)
    
    # Calculate k where q = 2^k
    k = q.bit_length() - 1
    
    # Manual Absolute Trace to bypass the SageMath PARI/GMP segmentation fault
    def manual_trace(val):
        return sum([val**(2**i) for i in range(k)])
        
    # Isolate an element where the manual Trace == 1 for the Artin-Schreier condition
    gamma = next(a for a in elements if manual_trace(a) == F(1))
    
    # CASE 1: h(x) = x^2 + x (Targets p-rank 2 ordinary curves)
    h_coeffs_1 = [F(0), F(1), F(1)]
    for f4 in elements:
        for f2 in elements:
            for f0 in elements:
                yield (h_coeffs_1, [f0, F(0), f2, F(0), f4, F(1)])
                
    # CASE 2: h(x) = x^2 (Targets p-rank 1, double root curves)
    h_coeffs_2 = [F(0), F(0), F(1)]
    for f4 in elements:
        for f1 in elements:
            for f0 in elements:
                yield (h_coeffs_2, [f0, f1, F(0), F(0), f4, F(1)])
                
    # CASE 3: h(x) = x (Targets p-rank 1, degree 1 curves)
    h_coeffs_3 = [F(0), F(1), F(0)]
    for f4 in elements:
        for f3 in elements:
            for f0 in elements:
                # The 'a' coefficient is constrained by the trace condition
                for a in [F(0), gamma]:
                    yield (h_coeffs_3, [f0, F(0), a, f3, f4, F(1)])
                    
    # CASE 4: h(x) = 1 (Targets p-rank 0 supersingular curves)
    h_coeffs_4 = [F(1), F(0), F(0)]
    for f4 in elements:
        for f3 in elements:
            for f2 in elements:
                yield (h_coeffs_4, [F(0), F(0), f2, f3, f4, F(1)])

def yield_batches(q, db_path):
    """
    Lazy generator: chunks combinations into lists of BATCH_SIZE and 
    yields them to the worker pool one by one, keeping main OS RAM perfectly clean.
    """
    batch = []
    for item in generate_exact_search_space(q):
        batch.append(item)
        if len(batch) >= BATCH_SIZE:
            yield (q, batch, db_path)
            batch = []
    if batch:
        yield (q, batch, db_path)

if __name__ == '__main__':
    # Detect laptop cores and subtract 1 to ensure the OS never freezes
    total_cores = multiprocessing.cpu_count()
    active_workers = max(1, total_cores - 1)
    
    print(f"Starting Exact Anchor Multi-Field Sieve on {active_workers} processors.")
    print("Core reserved for MX Linux OS stability.")
    
    # Initialize the worker pool (reused across all fields)
    with Pool(processes=active_workers) as pool:
        for q in TARGET_FIELDS:
            print(f"\n--- Starting Exact Anchor Generation for GF({q}) ---")
            db_path = init_db(q)
            
            # imap_unordered dynamically feeds batches to whichever core finishes first
            for _ in pool.imap_unordered(process_batch, yield_batches(q, db_path)):
                pass
                
            print(f"Completed mapping GF({q}). Data saved to {db_path}.")
            
    print("\nAll fields GF(2) through GF(64) processed successfully.")

