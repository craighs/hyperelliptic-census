import sqlite3
import time
import sys
import gc
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed

def worker_batch(f3_idx, missing_dict_snapshot, valid_a1_set, Q, db_name):
    try:
        from sage.all import GF, PolynomialRing
        
        Q2 = Q**2
        F = GF(Q, 'z')
        F2 = GF(Q2, 'w')
        F_elements = list(F)
        F2_elements = list(F2)
        
        def to_int(e):
            return sum(int(c)*(2**i) for i, c in enumerate(e.polynomial().list()))
            
        int_to_elem = {to_int(e): e for e in F_elements}
        
        mult_table = [[0]*Q for _ in range(Q)]
        square_table = [0]*Q
        trace_table = [0]*Q
        
        for e1 in F_elements:
            i1 = to_int(e1)
            trace_table[i1] = int(e1.trace())
            square_table[i1] = to_int(e1**2)
            for e2 in F_elements:
                mult_table[i1][to_int(e2)] = to_int(e1 * e2)
                
        ONE = to_int(F(1))
        ZERO = 0
        
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
        from_F2 = {v: k for k, v in to_F2.items()} # [CRITICAL PATCH: REVERSE MAP]
            
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
        
        inv_hx2_table = []
        for h in h_forms:
            row = [0]*Q
            for x in F_elements:
                val = h(x)
                if val != F(0):
                    row[to_int(x)] = to_int(~(val**2))
            inv_hx2_table.append(row)
            
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
                    V_list = []
                    for j in range(6):
                        X = (w**j) * inv_hw2
                        rel_X = X + X**Q  # [CRITICAL PATCH: RELATIVE TRACE]
                        V_list.append(from_F2[rel_X])
                    v_row.append(tuple(V_list))
            hw_is_zero.append(z_row)
            V_matrix.append(v_row)
            
        local_found = []
        audit = {'total': 0, 'singular': 0, 'matched': 0}
        
        f3 = to_int(F_elements[f3_idx])
        f4_forms = [ZERO, DELTA]
        f3_2 = to_F2[f3]
        mult = mult_table
        trace = trace_table
        square = square_table
        
        print(f"[Worker f3={f3_idx}] Booted. Tables initialized. Beginning sieve...", flush=True)

        for f2 in range(Q):
            f2_2 = to_F2[f2]
            for f1 in range(Q):
                f1_2 = to_F2[f1]
                for f0 in range(Q):
                    f0_2 = to_F2[f0]
                    for h_idx in range(5):
                        valid_f4s = [ZERO] if h_idx == 4 else f4_forms
                        for f4 in valid_f4s:
                            if h_idx == 4 and f2 != ZERO: continue 
                            audit['total'] += 1
                            
                            # MEMORY & LOGGING INTERCEPT
                            if audit['total'] % 50000 == 0:
                                gc.collect()  # Flush Sage Pari/FLINT C-objects to prevent RAM lockup
                                print(f"[Worker f3={f3_idx}] Sifted {audit['total']} curves. Local matches: {audit['matched']}", flush=True)

                            is_singular = False
                            if h_idx == 0:
                                if (f0 ^ square[f1] == ZERO) or ((f0 ^ f1 ^ f2 ^ f3 ^ f4 ^ ONE) ^ square[f1 ^ f3 ^ ONE] == ZERO): is_singular = True
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
                                
                            N1 = 1
                            inv_hx2_row = inv_hx2_table[h_idx]
                            for i in range(Q):
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
                                    if trace[c] == 0: N1 += 2
                                        
                            a1 = Q + 1 - N1
                            if a1 not in valid_a1_set: continue
                                
                            N2 = 1
                            z_row = hw_is_zero[h_idx]
                            v_row = V_matrix[h_idx]
                            for i in range(Q2):
                                if z_row[i]:
                                    N2 += 1
                                else:
                                    V = v_row[i]
                                    rel_trace = V[5] ^ mult[f4][V[4]] ^ mult[f3][V[3]] ^ mult[f2][V[2]] ^ mult[f1][V[1]] ^ mult[f0][V[0]]
                                    if trace[rel_trace] == 0: N2 += 2
                                        
                            a2 = (N2 - Q**2 - 1 + a1**2) // 2
                            N = 1 - (Q + 1) * a1 + a2 + Q**2
                            group_str = str(N)
                            
                            if group_str in missing_dict_snapshot:
                                audit['matched'] += 1
                                row_id = missing_dict_snapshot[group_str]
                                h_poly = h_forms[h_idx]
                                f_poly = R([int_to_elem[f0], int_to_elem[f1], int_to_elem[f2], int_to_elem[f3], int_to_elem[f4], F(1)])
                                local_found.append((row_id, str(h_poly), str(f_poly), "PENDING", group_str))
                                
        print(f"[Worker f3={f3_idx}] FINISHED! Total sifted: {audit['total']}. Matches: {audit['matched']}", flush=True)
        return local_found, audit
    except Exception as e:
        print(f"[Worker f3={f3_idx}] CRASHED: {e}", flush=True)
        return [], None

class LoggerWriter:
    def __init__(self, logger_level):
        self.logger_level = logger_level
    def write(self, message):
        if message != '\n':
            self.logger_level(message)
    def flush(self):
        pass

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("Usage: sage run_memory_safe_sieve.py <Q>")
        
    Q = int(sys.argv[1])
    db_name = f"gf{Q}_curves.db"
    log_name = f"sieve_workers_{Q}.log"

    # Set up master logging to tee to both file and console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(message)s',
        handlers=[
            logging.FileHandler(log_name, mode='a'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Redirect print statements to the logger so worker outputs are captured
    sys.stdout = LoggerWriter(logging.info)
    sys.stderr = LoggerWriter(logging.error)
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT c.id, c.group_order, c.a1 FROM curves c LEFT JOIN explicit_curves e ON c.id = e.id WHERE e.id IS NULL AND c.group_order IS NOT NULL")
    missing_rows = cursor.fetchall()
    
    missing_dict = {str(row[1]).strip(): row[0] for row in missing_rows}
    valid_a1_set = set(int(row[2]) for row in missing_rows if row[2] is not None)
    total_missing = len(missing_dict)
    
    print(f"=== INITIALIZING MEMORY-SAFE SIEVE OVER GF({Q}) ===")
    print(f"Loaded {total_missing} missing GF({Q}) targets.")
    
    found = 0
    start_time = time.time()
    master_audit = {'total': 0, 'singular': 0, 'matched': 0}

    # Left at 4 workers. Memory per worker is now clamped.
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = []
        for f3_idx in range(Q):
            futures.append(executor.submit(worker_batch, f3_idx, dict(missing_dict), valid_a1_set, Q, db_name))
            
        for future in as_completed(futures):
            result = future.result()
            if not result or result[1] is None: continue
            results, worker_audit = result
            for k in master_audit: master_audit[k] += worker_audit[k]
            
            for row_id, h_str, f_str, inv_str, group_str in results:
                if group_str in missing_dict:
                    missing_dict.pop(group_str)
                    print(f"  >>> GLOBAL MATCH SECURED: {group_str} (Total found: {found + 1}/{total_missing})", flush=True)
                    cursor.execute("INSERT OR REPLACE INTO explicit_curves (id, h_poly, f_poly, invariant_factors) VALUES (?, ?, ?, ?)", (row_id, h_str, f_str, inv_str))
                    found += 1
                    conn.commit()

    conn.close()
    print(f"\n=== F_{Q} AUDIT COMPLETE ===")
    print(f"Evaluated: {master_audit['total']:,}")
    print(f"Singular:  {master_audit['singular']:,}")
    print(f"Matched:   {master_audit['matched']:,}")
    print(f"Time:      {time.time() - start_time:.1f}s")
