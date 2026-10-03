import sqlite3
import os

# Create the master database
master_conn = sqlite3.connect('gf_master.db')
master_cursor = master_conn.cursor()

# Create the unified tables
master_cursor.execute('''CREATE TABLE IF NOT EXISTS curves (
    id INTEGER PRIMARY KEY,
    q INTEGER, 
    a1 INTEGER,
    a2 INTEGER,
    target_order INTEGER
)''')

master_cursor.execute('''CREATE TABLE IF NOT EXISTS explicit_curves (
    id INTEGER,
    h_poly TEXT,
    f_poly TEXT,
    geometric_order INTEGER,
    invariant_factors TEXT,
    FOREIGN KEY(id) REFERENCES curves(id)
)''')

master_id_counter = 1

for k in range(1, 7):
    q_val = 2**k
    db_name = f'gf{q_val}_curves.db'
    if not os.path.exists(db_name):
        print(f"Skipping {db_name}, not found.")
        continue
        
    print(f"Merging {db_name} (q={q_val})...")
    local_conn = sqlite3.connect(db_name)
    local_cursor = local_conn.cursor()
    
    # Check what columns actually exist in the local curves table
    local_cursor.execute("PRAGMA table_info(curves)")
    columns = [col[1] for col in local_cursor.fetchall()]
    
    if 'target_order' in columns:
        local_cursor.execute("SELECT id, a1, a2, target_order FROM curves")
        curves_data = local_cursor.fetchall()
    else:
        # Fallback for older schemas: compute target_order on the fly
        local_cursor.execute("SELECT id, a1, a2 FROM curves")
        curves_data = []
        for row in local_cursor.fetchall():
            c_id, a1, a2 = row
            # Compute theoretical geometric group order N = q^2 + 1 + a1(q + 1) + a2
            target_order = (q_val**2) + 1 + a1 * (q_val + 1) + a2
            curves_data.append((c_id, a1, a2, target_order))
    
    for row in curves_data:
        local_id, a1, a2, target_order = row
        
        # Insert into master curves table with explicit q value
        master_cursor.execute('''INSERT INTO curves (id, q, a1, a2, target_order) 
                                 VALUES (?, ?, ?, ?, ?)''', 
                              (master_id_counter, q_val, a1, a2, target_order))
                              
        # Get matching explicit curves
        local_cursor.execute('''SELECT h_poly, f_poly, geometric_order, invariant_factors 
                                FROM explicit_curves WHERE id = ?''', (local_id,))
        explicit_data = local_cursor.fetchall()
        
        for exp_row in explicit_data:
            h_poly, f_poly, geom_order, inv_factors = exp_row
            master_cursor.execute('''INSERT INTO explicit_curves 
                                     (id, h_poly, f_poly, geometric_order, invariant_factors) 
                                     VALUES (?, ?, ?, ?, ?)''', 
                                  (master_id_counter, h_poly, f_poly, geom_order, inv_factors))
                                  
        master_id_counter += 1
        
    local_conn.close()

master_conn.commit()
master_conn.close()
print("Merge complete! Master database successfully saved as gf_master.db.")
