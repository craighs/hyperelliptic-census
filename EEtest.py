import sqlite3
import math

db_name = "gf64_curves.db"
q = 64

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

cursor.execute("SELECT id, group_order, a1 FROM curves WHERE group_order IS NOT NULL")
rows = cursor.fetchall()

total_ExE = 0

for row in rows:
    row_id, N_str, a1_str = row
    N = int(N_str)
    a1 = int(a1_str)
    
    # CORRECTED MATH: + (q+1)*a1
    a2 = N - q**2 - 1 + (q + 1) * a1
    
    # The E x E Discriminant Test
    delta = a1**2 - 4 * (a2 - 2 * q)
    
    if delta >= 0:
        root = math.isqrt(delta)
        if root * root == delta:
            total_ExE += 1

print(f"Total E x E Isogeny Classes mathematically forced: {total_ExE}")
