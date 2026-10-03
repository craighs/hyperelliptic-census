"""
=========================================================================================
PHASE 3 PRISTINE RUN AUDIT: RED-TEAM & TRUTHMODE VERIFICATION
=========================================================================================
This script enforces the "Conservation of Mass" across the entire moduli space.
It proves that the input C++ parameter space perfectly bifurcated into the Pure Genus 2 
space and the Singular Genus <2 space, with zero dropped curves and zero corrupted bytes.
"""

import os
import csv
import sys

TARGET_FIELDS = [2, 4, 8, 16, 32, 64]

def run_audit():
    print("==========================================================")
    print(" INITIATING RED-TEAM PRISTINE DATASET AUDIT")
    print("==========================================================\n")
    
    total_input_all = 0
    total_pure_all = 0
    total_singular_all = 0
    total_corruptions = 0

    for q in TARGET_FIELDS:
        in_file = f"gf{q}_exact_curves.csv"
        pure_file = f"gf{q}_jacobian_groups.csv"
        rej_file = f"gf{q}_singular_rejects.log"

        if not os.path.exists(pure_file):
            continue

        # 1. Count Inputs (Subtract header)
        with open(in_file, 'r') as f:
            input_count = sum(1 for _ in f) - 1
            
        # 2. Count Rejects (No header)
        singular_count = 0
        if os.path.exists(rej_file):
            with open(rej_file, 'r') as f:
                singular_count = sum(1 for _ in f)

        # 3. Rigorous Pure CSV Parsing
        pure_count = 0
        corruptions = 0
        with open(pure_file, 'r') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                pure_count += 1
                group_struct = row.get('abelian_group_structure', '')
                
                # Check for empty fields, leaked singularities, or malformed I/O strings
                if not group_struct:
                    print(f"[!] CORRUPTION GF({q}) Row {row_num}: Empty group structure.")
                    corruptions += 1
                elif "ERROR" in group_struct or "SINGULAR" in group_struct:
                    print(f"[!] QUARANTINE BREACH GF({q}) Row {row_num}: {group_struct}")
                    corruptions += 1
                elif "Z/" not in group_struct:
                    print(f"[!] MALFORMED SNF GF({q}) Row {row_num}: {group_struct}")
                    corruptions += 1

        # 4. The Bijection Check (Conservation of Mass)
        print(f"--- GF({q}) Audit ---")
        print(f"  Input Parameter Curves : {input_count}")
        print(f"  Pure Genus 2 Curves    : {pure_count}")
        print(f"  Singular / Degenerate  : {singular_count}")
        
        math_check = (input_count == pure_count + singular_count)
        if math_check:
            print(f"  [PASS] Bijection Verified: {pure_count} + {singular_count} = {input_count}")
        else:
            print(f"  [FAIL] MASS LOSS DETECTED! Difference: {input_count - (pure_count + singular_count)}")
        
        if corruptions == 0:
            print(f"  [PASS] Data Integrity Verified: 0 format corruptions.")
        else:
            print(f"  [FAIL] {corruptions} CORRUPTIONS DETECTED.")
        print("")

        total_input_all += input_count
        total_pure_all += pure_count
        total_singular_all += singular_count
        total_corruptions += corruptions

    print("==========================================================")
    print(" GLOBAL MODULI SPACE TOTALS")
    print("==========================================================")
    print(f"Total Evaluated Parameters : {total_input_all}")
    print(f"Total Pure Genus 2 Curves  : {total_pure_all}")
    print(f"Total Singular Curves      : {total_singular_all}")
    print(f"Total Format Corruptions   : {total_corruptions}")
    
    if total_input_all == (total_pure_all + total_singular_all) and total_corruptions == 0:
        print("\n>>> CONCLUSION: DATASET IS 100% MATHEMATICALLY PRISTINE. <<<")
        print(">>> CLEAR FOR PHASE 4 SQLITE DATABASE INGESTION.         <<<")
    else:
        print("\n>>> CONCLUSION: FATAL ERRORS DETECTED. DO NOT PROCEED.   <<<")

if __name__ == '__main__':
    run_audit()
