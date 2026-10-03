import sqlite3

conn = sqlite3.connect("gf64_curves.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT c.group_order, e.h_poly, e.f_poly 
    FROM curves c
    JOIN explicit_curves e ON c.id = e.id
    ORDER BY c.group_order ASC
""")

rows = cursor.fetchall()
print(f"=== THE 22 RECOVERED TARGETS ===")
for r in rows:
    print(f"Group: {r[0]:<5} | h(x) = {r[1]:<20} | f(x) = {r[2]}")
conn.close()
