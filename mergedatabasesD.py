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
    
    # 1. Inspect curves table columns
    local_cursor.execute("PRAGMA table_info(curves)")
    curve_cols = [col[1] for col in local_cursor.fetchall()]
    
    if 'target_order' in curve_cols:
        local_cursor.execute("SELECT id, a1, a2, target_order FROM curves")
        curves_data = local_cursor.fetchall()
    else:
        local_cursor.execute("SELECT id, a1, a2 FROM curves")
        curves_data = []
        for row in local_cursor.fetchall():
            c_id, a1, a2 = row
            target_order = (q_val**2) + 1 + a1 * (q_val + 1) + a2
            curves_data.append((c_id, a1, a2, target_order))
            
    # 2. Inspect explicit_curves table columns dynamically
    local_cursor.execute("PRAGMA table_info(explicit_curves)")
    explicit_cols = [col[1] for col in local_cursor.fetchall()]
    
    select_fields = ["h_poly", "f_poly"]
    if 'geometric_order' in explicit_cols: select_fields.append("geometric_order")
    if 'invariant_factors' in explicit_cols: select_fields.append("invariant_factors")
    
    for row in curves_data:
        local_id, a1, a2, target_order = row
        
        # Insert into master curves table
        master_cursor.execute('''INSERT INTO curves (id, q, a1, a2, target_order) 
                                 VALUES (?, ?, ?, ?, ?)''', 
                              (master_id_counter, q_val, a1, a2, target_order))
                              
        query = f"SELECT {', '.join(select_fields)} FROM explicit_curves WHERE id = ?"
        local_cursor.execute(query, (local_id,))
        explicit_data = local_cursor.fetchall()
        
        for exp_row in explicit_data:
            # Safely extract based on what actually came back in the row tuple
            h_poly = exp_row[0] if len(exp_row) > 0 else None
            f_poly = exp_row[1] if len(exp_row) > 1 else None
            
            # Look for geometric_order and invariant_factors by column name matching
            geom_order = None
            inv_factors = None
            
            for idx, col_name in enumerate(select_fields):
                if col_name == 'geometric_order' and len(exp_row) > idx:
                    geom_order = exp_row[idx]
                elif col_name == 'invariant_factors' and len(exp_row) > idx:
                    inv_factors = exp_row[idx]
            
            master_cursor.execute('''INSERT INTO explicit_curves 
                                     (id, h_poly, f_poly, geometric_order, invariant_factors) 
                                     VALUES (?, ?, ?, ?, ?)''', 
                                  (master_id_counter, h_poly, f_poly, geom_order, inv_factors))
                                  
        master_id_counter += 1
        
    local_conn.close()

master_conn.commit()
master_conn.close()
print("Merge complete! Master database successfully saved as gf_master.db.")
