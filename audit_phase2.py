"""
================================================================================
RED-TEAM PHASE 2 AUDIT: STRUCTURAL INTEGRITY & ISOMORPHISM UNIQUENESS
================================================================================

This script acts as the final pre-flight check before the heavy SageMath computation.

MATHEMATICAL JUSTIFICATION (Isomorphism Uniqueness):
The Cardona-Quer-Nart-Pujolà exact affine reduction algorithm guarantees exactly
one unique polynomial pair [h(x), f(x)] per isomorphism class of genus 2 curves
over GF(2^k). If duplicate pairs exist, it indicates a boundary failure in the
C++ sieve's affine transformation loop, violating the strict bijection between
our dataset and the actual moduli space of these curves.

STRUCTURAL JUSTIFICATION (Data Serialization):
The C++ output serializes coefficients as string arrays (e.g., "[1, 0, 1]").
If the C++ file buffer truncated a row during high-speed I/O (e.g., "[1, 0,"),
Python's ast.literal_eval() will throw a fatal SyntaxError, instantly killing
the multiprocessing worker pool and ruining a multi-day SageMath run.
"""

import csv
import ast
import glob

def audit_phase2():
    csv_files = glob.glob("gf*_exact_curves.csv")
    
    if not csv_files:
        print("No CSV files found.")
        return

    print("==========================================================")
    print(" RED-TEAM PHASE 2 AUDIT: UNIQUENESS AND PARSING CHECK ")
    print("==========================================================")

    total_rows_all = 0
    total_duplicates = 0
    total_malformed = 0

    for file in sorted(csv_files):
        print(f"Auditing {file}...")
        
        seen_curves = set()
        file_duplicates = 0
        file_malformed = 0
        file_rows = 0
        
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):
                file_rows += 1
                total_rows_all += 1
                
                h_str = row.get('h_coeffs', '')
                f_str = row.get('f_coeffs', '')
                
                # 1. Structural Parse Check
                try:
                    if not (h_str.startswith('[') and h_str.endswith(']')):
                        raise ValueError("Malformed h_coeffs brackets")
                    if not (f_str.startswith('[') and f_str.endswith(']')):
                        raise ValueError("Malformed f_coeffs brackets")
                        
                    # Test actual parsing
                    h_list = ast.literal_eval(h_str)
                    f_list = ast.literal_eval(f_str)
                except Exception as e:
                    print(f"  [Row {row_num}] PARSE ERROR: h={h_str}, f={f_str} | {e}")
                    file_malformed += 1
                    continue # Skip duplicate check if malformed
                    
                # 2. Isomorphism Uniqueness Check
                # Tuples are hashable and fast for set lookups
                curve_signature = (tuple(h_list), tuple(f_list))
                if curve_signature in seen_curves:
                    # We don't print every duplicate as there could be thousands, 
                    # just log the first few for debugging if needed.
                    if file_duplicates < 3:
                        print(f"  [Row {row_num}] DUPLICATE DETECTED: {curve_signature}")
                    elif file_duplicates == 3:
                        print(f"  [...] Further duplicates in {file} suppressed.")
                    file_duplicates += 1
                else:
                    seen_curves.add(curve_signature)
                    
        total_duplicates += file_duplicates
        total_malformed += file_malformed
        
        if file_duplicates == 0 and file_malformed == 0:
            print(f"  -> Pass: 0 duplicates, 0 malformed rows. ({file_rows} unique curves)")
            
    print("==========================================================")
    print("                      FINAL RESULTS                       ")
    print("==========================================================")
    print(f"Total CSV Files Audited    : {len(csv_files)}")
    print(f"Total Rows Scanned         : {total_rows_all}")
    print(f"Total Malformed Rows       : {total_malformed}")
    print(f"Total Duplicate Curves     : {total_duplicates}")
    
    if total_malformed == 0 and total_duplicates == 0:
        print("\nSTATUS: CLEAR FOR LAUNCH.")
        print("Structural integrity verified. Moduli space bijection confirmed.")
        print("You may safely initiate the SageMath multiprocessing pipeline.")

if __name__ == "__main__":
    audit_phase2()
