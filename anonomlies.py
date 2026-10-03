import sqlite3
import re

conn = sqlite3.connect('hyperelliptic_census.db')
cursor = conn.cursor()

cursor.execute("SELECT id, geometric_order, invariant_factors FROM explicit_curves WHERE invariant_factors IS NOT NULL")

product_anomalies = 0
snf_anomalies = 0

for row_id, geometric_order, group_str in cursor.fetchall():
    # Use regex to extract all numbers trapped between "Z/" and "Z"
    # Example: "Z/2Z x Z/2Z x Z/947Z" -> [2, 2, 947]
    factors = [int(n) for n in re.findall(r'Z/(\d+)Z', group_str)]
    
    if not factors:
        continue
        
    # 1. Check Product against the newly patched geometric_order
    product = 1
    for n in factors:
        product *= n
        
    if product != geometric_order:
        print(f"PRODUCT FAIL: Curve {row_id} | Order {geometric_order} != Product {product} | {group_str}")
        product_anomalies += 1
        
    # 2. Check SNF Divisibility (n_i divides n_{i+1})
    for i in range(len(factors) - 1):
        if factors[i+1] % factors[i] != 0:
            snf_anomalies += 1
            break # We only need to count the curve once if it breaks SNF

print("\n--- FINAL AUDIT RESULTS ---")
print(f"Product Anomalies (Missing Points): {product_anomalies}")
print(f"SNF Divisibility Failures (Unreduced by SageMath): {snf_anomalies}")
