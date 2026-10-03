import sqlite3
import math

db_name = "gf64_curves.db"
q = 64

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Ensure the geometry_type column exists
try:
    cursor.execute("ALTER TABLE curves ADD COLUMN geometry_type TEXT")
except sqlite3.OperationalError:
    pass # Column already exists

cursor.execute("SELECT id, group_order, a1 FROM curves WHERE group_order IS NOT NULL")
rows = cursor.fetchall()

tagged_ExE = 0
tagged_Jacobian = 0
tagged_Unknown = 0

for row in rows:
    row_id, N_str, a1_str = row
    
    # Force the database strings into integers
    N = int(N_str)
    a1 = int(a1_str)
    
    # Calculate a2 from the group order N
    # N = q^2 + 1 + (q+1)*a1 + a2
    a2 = N - q**2 - 1 - (q + 1) * a1
    
    # The E x E Discriminant Test
    delta = a1**2 - 4 * (a2 - 2 * q)
    
    is_ExE = False
    if delta >= 0:
        root = math.isqrt(delta)
        if root * root == delta:
            is_ExE = True
            
    # Check if we explicitly found this curve
    cursor.execute("SELECT id FROM explicit_curves WHERE id = ?", (row_id,))
    is_jacobian = cursor.fetchone() is not None
    
    # Assign Geometry Type
    if is_jacobian:
        geo_type = "Jacobian"
        tagged_Jacobian += 1
    elif is_ExE:
        geo_type = "E x E"
        tagged_ExE += 1
    else:
        geo_type = "Non-Jacobian"
        tagged_Unknown += 1
        
    cursor.execute("UPDATE curves SET geometry_type = ? WHERE id = ?", (geo_type, row_id))

conn.commit()
conn.close()

print(f"Classification complete for {db_name}:")
print(f"  Explicit Jacobians: {tagged_Jacobian}")
print(f"  E x E (Splits):     {tagged_ExE}")
print(f"  Non-Jacobians:      {tagged_Unknown}")
