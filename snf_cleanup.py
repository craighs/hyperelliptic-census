import sqlite3
import re
from math import gcd

# Python 3.9+ has math.lcm, but we write it manually for cross-compatibility
def lcm(a, b):
    return (a * b) // gcd(a, b)

def to_snf(factors):
    f = list(factors)
    changed = True
    while changed:
        changed = False
        for i in range(len(f)):
            for j in range(i + 1, len(f)):
                if f[j] % f[i] != 0:
                    g = gcd(f[i], f[j])
                    l = lcm(f[i], f[j])
                    if f[i] != g or f[j] != l:
                        f[i], f[j] = g, l
                        changed = True
    # Filter out 1s (trivial groups) and sort the factors
    return sorted([x for x in f if x > 1])

# Connect to database
conn = sqlite3.connect('hyperelliptic_census.db')
cursor = conn.cursor()

print("Fetching data from explicit_curves...")
cursor.execute("SELECT id, invariant_factors FROM explicit_curves WHERE invariant_factors LIKE '%Z%'")
rows = cursor.fetchall()

updates = []
for row_id, group_str in rows:
    # 1. Extract pure integers from the "Z/nZ" string
    factors = [int(n) for n in re.findall(r'Z/(\d+)Z', group_str)]
    
    # 2. Compress into strict Smith Normal Form
    snf_list = to_snf(factors)
    
    # 3. Format as a clean string like "[2, 1894]"
    clean_str = str(snf_list)
    updates.append((clean_str, row_id))

print(f"Compressing and fixing {len(updates)} rows...")

# Bulk update the database
cursor.executemany("UPDATE explicit_curves SET invariant_factors = ? WHERE id = ?", updates)
conn.commit()
conn.close()

print("Database cleanup complete! All group topologies are now strictly formatted SNF arrays.")
