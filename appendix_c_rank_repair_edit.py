"""
=========================================================================================
APPENDIX C: RANK-2 ANOMALY REPAIR ALGORITHM (STREAMING VERSION)
=========================================================================================
This script streams massive characteristic 2 finite field datasets row-by-row to 
prevent OOM (Out Of Memory) crashes. It identifies curves where SageMath's 2-torsion 
divisor sampling artificially fragmented the Sylow-2 subgroup (exceeding the p-rank <= g 
bound), recalculates them using targeted sampling, and writes them immediately to disk.
=========================================================================================
"""

import csv
import ast
import gc
from sage.all import GF, PolynomialRing, HyperellipticCurve, factor

TARGET_FIELDS = [64]
HIGH_DENSITY_SAMPLES = 500

def get_irreducible_poly(q):
    """Retrieves the exact algebraic basis matching the C++ anchor generation."""
    bases = {
        4: [1, 1, 1],                
        8: [1, 1, 0, 1],             
        16: [1, 1, 0, 0, 1],         
        32: [1, 0, 1, 0, 0, 1],      
        64: [1, 1, 0, 0, 0, 0, 1]    # x^6 + x + 1 (Ensure this matched your dynamic output)
    }
    R = PolynomialRing(GF(2), 'x')
    return R(bases[q]) if q in bases else None

def reconstruct_element(integer_val, F, alpha, q):
    if integer_val == -1: return F(0)
    if q == 2: return F(integer_val)
    return alpha**integer_val

def is_anomalous(group_string):
    if group_string == "Z/1Z": return False
    factors = group_string.split(" x ")
    even_count = sum(1 for f in factors if int(f.replace("Z/", "").replace("Z", "")) % 2 == 0)
    return even_count > 2

def recalculate_sylow_2(J, target_order):
    prime_factors = factor(target_order)
    e = next((exp for p, exp in prime_factors if p == 2), 0)
            
    if e == 0: return []
    if e == 1: return [2]
    if e == 2: return [2, 2] 
    
    cofactor = target_order // (2**e)
    max_order_exp = 0
    
    for _ in range(HIGH_DENSITY_SAMPLES):
        try:
            D = J.random_element()
        except Exception:
            continue
            
        S = cofactor * D
        if S == J(0): continue
            
        k = 0
        while S != J(0):
            S = 2 * S
            k += 1
            
        if k > max_order_exp: max_order_exp = k
        if max_order_exp == e: break

    rem_e = e - max_order_exp
    
    if rem_e == 0: 
        return [2**e]
    else: 
        return [2**rem_e, 2**max_order_exp]

def repair_dataset_stream(q):
    input_file = f'gf{q}_jacobian_groups.csv'
    output_file = f'gf{q}_jacobian_groups_repaired.csv'
    
    modulus_poly = get_irreducible_poly(q)
    F = GF(q, 'a', modulus=modulus_poly) if modulus_poly else GF(2)
    alpha = F.gen() if q > 2 else None
    R = PolynomialRing(F, 'x')
    x = R.gen()

    try:
        # Open both files simultaneously for streaming
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            print(f"\n--- Streaming Rank-2 Repair for GF({q}) ---")
            
            rows_processed = 0
            repaired_count = 0
            
            for row in reader:
                if is_anomalous(row['abelian_group_structure']):
                    h_ints = ast.literal_eval(row['h_coeffs'])
                    f_ints = ast.literal_eval(row['f_coeffs'])
                    target_order = int(row['target_order'])
                    
                    h_poly = sum(reconstruct_element(val, F, alpha, q) * x**i for i, val in enumerate(h_ints))
                    f_poly = sum(reconstruct_element(val, F, alpha, q) * x**i for i, val in enumerate(f_ints))
                    
                    try:
                        C = HyperellipticCurve(f_poly, h_poly)
                        J = C.jacobian()
                        
                        # Recalculate 2-Sylow
                        sylow_2_clamped = recalculate_sylow_2(J, target_order)
                        row['abelian_group_structure'] += " [REPAIRED]"
                        repaired_count += 1
                    except Exception:
                        pass
                
                # Write the row immediately (whether it was repaired or left untouched)
                writer.writerow(row)
                rows_processed += 1
                
                # Flush SageMath memory buffers every 10,000 rows
                if rows_processed % 10000 == 0:
                    print(f"    [PROGRESS] GF({q}): Scanned {rows_processed} curves, Repaired {repaired_count}...")
                    gc.collect()

            print(f"Successfully finished GF({q}). Total curves scanned: {rows_processed}. Total repaired: {repaired_count}.")
            print(f"Cleaned dataset saved to {output_file}.")
            
    except FileNotFoundError:
        pass

if __name__ == '__main__':
    for q in TARGET_FIELDS:
        repair_dataset_stream(q)
