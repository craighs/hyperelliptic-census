import sqlite3
import time
import itertools
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

def worker_batch(f3_idx, missing_dict_snapshot, valid_a1_set):
    sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] Worker {f3_idx}: Booting up and loading Sage...\n")
    sys.stderr.flush()
    
    try:
        from sage.all import GF, PolynomialRing
        
        q_val = 64
        F = GF(q_val, 'z')
        F2 = GF(q_val**2, 'w')
        F_elements = list(F)
        F2_elements = list(F2)
        
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] Worker {f3_idx}: Building Integer Lookup Tables...\n")
        sys.stderr.flush()
        
        # 1. BIJECTIVE INTEGER MAPPING (0...63)
        def to_int(e):
            return sum(int(c)*(2**i) for i, c in enumerate(e.polynomial().list()))
            
        int_to_elem = {to_int(e): e for e in F_elements}
        
        mult_table = [[0]*64 for _ in range(64)]
        square_table = [0]*64
        trace_table = [0]*64
        
        for e1 in F_elements:
            i1 = to_int(e1)
            trace_table[i1] = int(e1.trace())
            square_table[i1] = to_int(e1**2)
            for e2 in F_elements:
                mult_table[i1][to_int(e2)] = to_int(e1 * e2)
                
        ONE = to_int(F(1))
        ZERO = 0
        
        # 2. GALOIS EMBEDDING
        mod_coeffs_F2 = [F2(int(c)) for c in F.modulus().list()]
        r = None
        for w in F2_elements:
            if sum((c * (w**i) for i, c in enumerate(mod_coeffs_F2)), F2(0)) == F2(0):
                r = w
                break
                
        map_to_F2 = {}
        for c in F_elements:
            coeffs = c.polynomial().list()
            map_to_F2[c] = sum((F2(int(a)) * (r**i) for i, a in enumerate(coeffs)), F2(0))
            
        to_F2 = {to_int(e): map_to_F2[e] for e in F_elements}
            
        delta = next(d for d in F_elements if d != F(0) and int(d.trace()) == 1)
        DELTA = to_int(delta)
        
        R = PolynomialRing(F, 'x')
        h_forms = [
            R('x')**2 + R('x'),           
            R('x')**2 + R('x') + delta,   
            R('x')**2,                    
            R('x'),                       
            R(1)                          
        ]
        
        delta_F2 = map_to_F2[delta]
        h2_roots = [w for w in F2_elements if w**2 + w + delta_F2 == F2(0)]
        h2_roots_pow = [[r_val**j for j in range(6)] for r_val in h2_roots]
        
        # 3. N1 FAST INTEGER TABLES
        inv_hx2_table = []
        for h in h_forms:
            row = [0]*64
            for x in F_elements:
                val = h(x)
                if val != F(0):
                    row[to_int(x)] = to_int(~(val**2))
            inv_hx2_table.append(row)
            
        # 4. N2 RELATIVE TRACE TABLES (Compresses GF4096 to GF64 Integers)
        hw_is_zero = []
        V_matrix = []
        
        for h in h_forms:
            z_row = []
            v_row = []
            h_coeffs_F2 = [map_to_F2[c] for c in h.list()]
            for w in F2_elements:
                hw = sum((c * (w**i) for i, c in enumerate(h_coeffs_F2)), F2(0))
                if hw == F2(0):
                    z_row.append(True)
                    v_row.append((0,0,0,0,0,0))
                else:
                    z_row.append(False)
                    inv_hw2 = ~(hw**2)
                    # Maps trace all the way down to GF64 integers
                    V_tuple = tuple(to_int(((w**j)*inv_hw2).trace()) for j in range(6))
                    v_row.append(V_tuple)
            hw_is_zero.append(z_row)
            V_matrix.append(v_row)
            
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] Worker {f3_idx}: Math initialized. Starting PURE INTEGER Sieve...\n")
        sys.stderr.flush()
        
        local_found = []
        audit = {'total': 0, 'singular': 0, 'failed_N1': 0, 'failed_N2': 0, 'matched': 0}
        
        # Pre-cache local variables for absolute maximum inner-loop speed
        f3 = to_int(F_elements[f3_idx])
        f4_forms = [ZERO, DELTA]
        f3_2 = to_F2[f3]
        mult = mult_table
        trace = trace_table
        square = square_table
        
        # PURE INTEGER ITERATION
        for f2 in range(64):
            f2_2 = to_F2[f2]
            for f1 in range(64):
                f1_2 = to_F2[f1]
                for f0 in range(64):
                    f0_2 = to_F2[f0]
                    
                    for h_idx in range(5):
                        valid_f4s = [ZERO] if h_idx == 4 else f4_forms
                        
                        for f4 in valid_f4s:
                            if h_idx == 4 and f2 != ZERO:
                                continue 
                                
                            audit['total'] += 1
                            
                            if audit['total'] % 100000 == 0:
                                sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] Worker {f3_idx}: {audit['total']:,} evaluations complete...\n")
                                sys.stderr.flush()
                                
                            # --- 1. INSTANT INTEGER SINGULARITY CHECK ---
                            is_singular = False
                            if h_idx == 0:
                                if (f0 ^ square[f1] == ZERO) or ((f0 ^ f1 ^ f2 ^ f3 ^ f4 ^ ONE) ^ square[f1 ^ f3 ^ ONE] == ZERO):
                                    is_singular = True
                            elif h_idx == 1:
                                f4_2 = to_F2[f4]
                                for r_pow in h2_roots_pow:
                                    f_r = r_pow[5] + f4_2*r_pow[4] + f3_2*r_pow[3] + f2_2*r_pow[2] + f1_2*r_pow[1] + f0_2
                                    fp_r = r_pow[4] + f3_2*r_pow[2] + f1_2
                                    if f_r + fp_r**2 == F2(0):
                                        is_singular = True
                                        break
                            elif h_idx == 2:
                                if f1 == ZERO: is_singular = True
                            elif h_idx == 3:
                                if f0 ^ square[f1] == ZERO: is_singular = True
                                
                            if is_singular:
                                audit['singular'] += 1
                                continue
                                
                            # --- 2. N1 NATIVE INTEGER HORNER METHOD (Bypasses Sage) ---
                            N1 = 1
                            inv_hx2_row = inv_hx2_table[h_idx]
                            for i in range(64):
                                inv_hx2 = inv_hx2_row[i]
                                if inv_hx2 == ZERO:
                                    N1 += 1
                                else:
                                    v = i ^ f4
                                    v = mult[v][i] ^ f3
                                    v = mult[v][i] ^ f2
                                    v = mult[v][i] ^ f1
                                    v = mult[v][i] ^ f0
                                    c = mult[v][inv_hx2]
                                    if trace[c] == 0:
                                        N1 += 2
                                        
                            a1 = q_val + 1 - N1
                            if a1 not in valid_a1_set:
                                audit['failed_N1'] += 1
                                continue
                                
                            # --- 3. N2 NATIVE DOT PRODUCT (Bypasses GF4096 entirely) ---
                            N2 = 1
                            z_row = hw_is_zero[h_idx]
                            v_row = V_matrix[h_idx]
                            for i in range(4096):
                                if z_row[i]:
                                    N2 += 1
                                else:
                                    V = v_row[i]
                                    rel_trace = V[5] ^ mult[f4][V[4]] ^ mult[f3][V[3]] ^ mult[f2][V[2]] ^ mult[f1][V[1]] ^ mult[f0][V[0]]
                                    if trace[rel_trace] == 0:
                                        N2 += 2
                                        
                            a2 = (N2 - q_val**2 - 1 + a1**2) // 2
                            N = 1 - (q_val + 1) * a1 + a2 + q_val**2
                            group_str = str(N)
                            
                            if group_str in missing_dict_snapshot:
                                audit['matched'] += 1
                                row_id = missing_dict_snapshot[group_str]
                                h_poly = h_forms[h_idx]
                                f_poly = R([int_to_elem[f0], int_to_elem[f1], int_to_elem[f2], int_to_elem[f3], int_to_elem[f4], F(1)])
                                local_found.append((row_id, str(h_poly), str(f_poly), "PENDING", group_str))
                            else:
                                audit['failed_N2'] += 1
                                
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] Worker {f3_idx}: Finished chunk safely.\n")
        sys.stderr.flush()
        return local_found, audit

    except Exception as e:
        import traceback
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] Worker {f3_idx} FATAL ERROR: {e}\n{traceback.format_exc()}\n")
        sys.stderr.flush()
        return [], None

if __name__ == '__main__':
    db_name = "gf64_curves.db"
    num_workers = 4
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.id, c.group_order, c.a1 
        FROM curves c
        LEFT JOIN explicit_curves e ON c.id = e.id
        WHERE e.id IS NULL AND c.group_order IS NOT NULL
    """)
    missing_rows = cursor.fetchall()
    missing_dict = {str(row[1]).strip(): row[0] for row in missing_rows}
    valid_a1_set = set(int(row[2]) for row in missing_rows if row[2] is not None)
    total_missing = len(missing_dict)
    
    start_msg = f"Loaded {total_missing} missing targets. Starting Exhaustive Audit Sieve...\n"
    print(start_msg.strip())
    sys.stdout.flush()
    with open("sieve_progress.log", "w") as logfile:
        logfile.write(start_msg)

    found = 0
    chunks_completed = 0
    start_time = time.time()
    
    master_audit = {
        'total': 0, 'singular': 0, 'failed_N1': 0, 'failed_N2': 0, 'matched': 0
    }

    print(f"[{time.strftime('%H:%M:%S')}] Spawning worker processes...")
    sys.stdout.flush()

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for f3_idx in range(64):
            futures.append(executor.submit(worker_batch, f3_idx, dict(missing_dict), valid_a1_set))
            
        for future in as_completed(futures):
            chunks_completed += 1
            elapsed = time.time() - start_time
            
            result = future.result()
            if not result or result[1] is None:
                msg = f"[{time.strftime('%H:%M:%S')}] [{elapsed:.1f}s] Chunk {chunks_completed}/64 FAILED DUE TO FATAL ERROR.\n"
                print(msg.strip())
                continue
                
            results, worker_audit = result
            
            for k in master_audit:
                master_audit[k] += worker_audit[k]
            
            msg = (f"[{time.strftime('%H:%M:%S')}] [{elapsed:.1f}s] Chunk {chunks_completed}/64 | "
                   f"Eval: {worker_audit['total']:,} | "
                   f"Singular: {worker_audit['singular']:,} | "
                   f"Fail N1: {worker_audit['failed_N1']:,} | "
                   f"Fail N2: {worker_audit['failed_N2']:,} | "
                   f"Match: {worker_audit['matched']:,}\n")
            print(msg.strip())
            sys.stdout.flush()
            
            with open("sieve_progress.log", "a") as logfile:
                logfile.write(msg)
                
            for row_id, h_str, f_str, inv_str, group_str in results:
                if group_str in missing_dict:
                    missing_dict.pop(group_str)
                    match_msg = f"  >>> MATCH DETECTED! Found {found + 1} / {total_missing} | Group: {group_str}\n"
                    print(match_msg.strip())
                    sys.stdout.flush()
                    with open("sieve_progress.log", "a") as logfile:
                        logfile.write(match_msg)
                        
                    cursor.execute(
                        "INSERT OR REPLACE INTO explicit_curves (id, h_poly, f_poly, invariant_factors) VALUES (?, ?, ?, ?)",
                        (row_id, h_str, f_str, inv_str)
                    )
                    found += 1
                    conn.commit()

    conn.close()
    
    end_msg = (f"\n=== GLOBAL AUDIT SUMMARY ===\n"
               f"Total Curves Evaluated: {master_audit['total']:,}\n"
               f"Discarded (Singular):   {master_audit['singular']:,}\n"
               f"Discarded (Failed N1):  {master_audit['failed_N1']:,}\n"
               f"Discarded (Failed N2):  {master_audit['failed_N2']:,}\n"
               f"Total Targets Matched:  {master_audit['matched']:,}\n"
               f"Time Elapsed:           {time.time() - start_time:.1f}s\n")
    print(end_msg)
    with open("sieve_progress.log", "a") as logfile:
        logfile.write(end_msg)
