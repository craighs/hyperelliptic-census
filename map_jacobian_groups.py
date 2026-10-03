"""
=========================================================================================
JACOBIAN ABELIAN GROUP STRUCTURE MAPPING (GF(2) - GF(64))
=========================================================================================
Features Dynamic Basis Discovery: Probes the CSV data using Artin-Schreier 
point counting against the reversed Weil polynomial to deduce the EXACT 
irreducible polynomial used by C++/NTL. 
Tests the LAST 5 rows to avoid GF(2) subfield false positives.
=========================================================================================
"""

import csv
import ast
import gc
from sage.all import GF, PolynomialRing, HyperellipticCurve, factor

TARGET_FIELDS = [2, 4, 8, 16, 32, 64]
MAX_SAMPLING_ATTEMPTS = 75

def reconstruct_element(integer_val, F, alpha, q):
    """Reconstructs the element using primitive root exponents."""
    if integer_val == -1:
        return F(0)
    if q == 2:
        return F(integer_val)
    return alpha**integer_val

def get_irreducible_polys(k):
    """Generates all irreducible polynomials of degree k over GF(2)."""
    R = PolynomialRing(GF(2), 'x')
    irreducibles = []
    for i in range((1 << k) + 1, (1 << (k+1)), 2):
        coeffs = [(i >> j) & 1 for j in range(k+1)]
        p = R(coeffs)
        if p.is_irreducible():
            irreducibles.append(p)
    return irreducibles

def count_pts_fast(h_poly, f_poly, F_field):
    """Lightning-fast Artin-Schreier point counting."""
    pts = 1
    for x_val in F_field:
        hx = h_poly(x_val)
        fx = f_poly(x_val)
        if hx.is_zero():
            pts += 1
        else:
            c = fx / (hx**2)
            if c.trace().is_zero():
                pts += 2
    return pts

def discover_compatible_field(q, test_rows):
    """Finds the exact algebraic basis NTL used by matching the curve point counts."""
    if q == 2:
        return GF(2), None, PolynomialRing(GF(2), 'x').gen()
        
    k = q.bit_length() - 1
    print(f"    [INFO] Probing algebraic bases for GF({q}) with structural verification...")
    
    # Grab the LAST 5 rows to ensure we test complex primitive coefficients, not just 0 and 1
    sample_rows = test_rows[-5:] if len(test_rows) >= 5 else test_rows
    
    for poly in get_irreducible_polys(k):
        try:
            F = GF(q, 'a', modulus=poly)
            alpha = F.gen()
            R = PolynomialRing(F, 'x')
            x = R.gen()
            
            # The mapped element must be a primitive root
            if alpha.multiplicative_order() != q - 1:
                continue
                
            success = True
            for row in sample_rows: 
                h_ints = ast.literal_eval(row['h_coeffs'])
                f_ints = ast.literal_eval(row['f_coeffs'])
                target_order = int(row['target_order'])
                geometric_order = int(row['geometric_order'])
                
                # MATHEMATICAL EXTRACTION: Deduce exact curve points (N1) from CSV Weil data
                L_minus_1 = geometric_order // target_order
                a1 = (target_order - L_minus_1) // (2 * (q + 1))
                expected_N1 = a1 + q + 1
                
                h_poly = sum(reconstruct_element(val, F, alpha, q) * x**i for i, val in enumerate(h_ints))
                f_poly = sum(reconstruct_element(val, F, alpha, q) * x**i for i, val in enumerate(f_ints))
                
                # Compare curve points to curve points
                if count_pts_fast(h_poly, f_poly, F) != expected_N1:
                    success = False
                    break
                    
            if success:
                print(f"    [SUCCESS] Matched exact C++ isomorphism: {poly}")
                return F, alpha, x
        except Exception:
            continue
            
    raise ValueError(f"Could not find a compatible algebraic basis for GF({q}).")

def get_sylow_structure(J, p, e, cofactor):
    if e == 0: return []
    if e == 1: return [p]
        
    max_order_exp = 0
    for _ in range(MAX_SAMPLING_ATTEMPTS):
        try:
            D = J.random_element()
        except Exception:
            continue
            
        S = cofactor * D
        if S == J(0): continue
            
        k = 0
        while S != J(0):
            S = p * S
            k += 1
            
        if k > max_order_exp: max_order_exp = k
        if max_order_exp == e: break

    rem_e = e - max_order_exp
    if rem_e == 0: return [p**e]
    elif rem_e <= max_order_exp: return [p**rem_e, p**max_order_exp]
    else: return [p] * (rem_e - max_order_exp) + [p**max_order_exp, p**max_order_exp]

def compute_snf_group_structure(J, target_order):
    prime_factors = factor(target_order)
    sylow_components = []
    
    for p, e in prime_factors:
        cofactor = target_order // (p**e)
        sylow_structure = get_sylow_structure(J, p, e, cofactor)
        if sylow_structure: sylow_components.append(sylow_structure)
            
    if not sylow_components: return "Z/1Z"
        
    max_rank = max(len(comp) for comp in sylow_components)
    padded_components = []
    for comp in sylow_components:
        padding = [1] * (max_rank - len(comp))
        padded_components.append(padding + comp)
        
    snf_invariants = [1] * max_rank
    for comp in padded_components:
        for i in range(max_rank): snf_invariants[i] *= comp[i]
            
    return " x ".join(f"Z/{n}Z" for n in snf_invariants if n > 1)

def process_csv(q):
    input_file = f'gf{q}_exact_curves.csv'
    output_file = f'gf{q}_jacobian_groups.csv'
    
    try:
        with open(input_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        return

    print(f"\n--- Mapping Jacobian Groups for GF({q}) ---")
    
    F, alpha, x = discover_compatible_field(q, rows)
    
    with open(output_file, 'w', newline='') as f:
        fieldnames = reader.fieldnames + ['abelian_group_structure']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        curves_processed = 0
        
        for row in rows:
            h_ints = ast.literal_eval(row['h_coeffs'])
            f_ints = ast.literal_eval(row['f_coeffs'])
            target_order = int(row['target_order'])
            
            h_poly = sum(reconstruct_element(val, F, alpha, q) * x**i for i, val in enumerate(h_ints))
            f_poly = sum(reconstruct_element(val, F, alpha, q) * x**i for i, val in enumerate(f_ints))
            
            try:
                C = HyperellipticCurve(f_poly, h_poly)
                J = C.jacobian()
                
                group_structure = compute_snf_group_structure(J, target_order)
                row['abelian_group_structure'] = group_structure
                writer.writerow(row)
                
            except Exception as e:
                print(f"Failed analysis on curve {h_ints}, {f_ints}: {e}")
                
            curves_processed += 1
            if curves_processed % 2000 == 0:
                print(f"    [PROGRESS] GF({q}): Mapped {curves_processed} group structures...")
                gc.collect() 

    print(f"Completed mapping GF({q}). Total curves processed: {curves_processed}. Data saved to {output_file}.")

if __name__ == '__main__':
    for q in TARGET_FIELDS:
        process_csv(q)
    print("\nAll fields GF(2) through GF(64) mapped successfully.")
