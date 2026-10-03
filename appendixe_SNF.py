import sqlite3
import ast

conn = sqlite3.connect('hyperelliptic_census.db')
cursor = conn.cursor()

cursor.execute("SELECT id, geometric_order, invariant_factors FROM explicit_curves WHERE invariant_factors IS NOT NULL")

anomalies = 0
for row_id, geometric_order, snf_str in cursor.fetchall():
    try:
        # Convert string "[2, 2, 4]" into a Python list
        snf_list = ast.literal_eval(snf_str)
        
        # 1. Check Product
        product = 1
        for n in snf_list:
            product *= n
            
        if product != geometric_order:
            print(f"FAIL: Curve ID {row_id} | Order {geometric_order} != SNF Product {product} | SNF: {snf_str}")
            anomalies += 1
            
        # 2. Check Divisibility (n_i divides n_{i+1})
        for i in range(len(snf_list) - 1):
            if snf_list[i+1] % snf_list[i] != 0:
                print(f"FAIL: Curve ID {row_id} | SNF Divisibility Broken: {snf_list[i]} does not divide {snf_list[i+1]}")
                anomalies += 1
                
    except Exception as e:
        print(f"FAIL: Curve ID {row_id} | Corrupt SNF string format: {snf_str}")
        anomalies += 1

print(f"Audit Complete. Total Anomalies Found: {anomalies}")
