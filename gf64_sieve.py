import sys
import traceback
import sqlite3
import time

print(">>> SCRIPT STARTED: Python interpreter is running.", flush=True)

try:
    from sage.all import *
    print(">>> SageMath libraries and modules imported successfully.", flush=True)

    db_name = "gf64_curves.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS curves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            f_poly TEXT,
            h_poly TEXT,
            l_poly TEXT,
            timestamp REAL
        )
    ''')
    conn.commit()
    print(">>> SQLite database initialized successfully.", flush=True)

    print(">>> Setting up F_64 finite field...", flush=True)
    q = 64
    F = GF(q, name='a')
    a = F.gen()
    R = PolynomialRing(F, 'x')
    x = R.gen()
    print(f">>> F_64 and polynomial ring initialized successfully. Field order: {F.cardinality()}", flush=True)

    print(f"Database connected. Starting F_{q} curve enumeration...", flush=True)
    
    valid_count = 0
    batch_data = []
    start_time = time.time()
    
    # Representative scan utilizing canonical coefficient limits
    for h2 in [F(0), F(1)]:
        for h1 in F:
            for h0 in F:
                h = h2*(x**2) + h1*x + h0
                if h.is_zero():
                    continue
                    
                for f5 in [F(1)]:
                    for f4 in F:
                        for f3 in F:
                            for f2 in F:
                                for f1 in F:
                                    for f0 in F:
                                        f = f5*(x**5) + f4*(x**4) + f3*(x**3) + f2*(x**2) + f1*x + f0
                                        
                                        try:
                                            C = HyperellipticCurve(f, h)
                                            if C.is_smooth():
                                                poly = C.l_polynomial()
                                                batch_data.append((str(f), str(h), str(poly), time.time()))
                                                valid_count += 1
                                                
                                                if len(batch_data) >= 1000:
                                                    cursor.executemany('''
                                                        INSERT INTO curves (f_poly, h_poly, l_poly, timestamp)
                                                        VALUES (?, ?, ?, ?)
                                                    ''', batch_data)
                                                    conn.commit()
                                                    batch_data = []
                                                    
                                                if valid_count > 0 and valid_count % 1000 == 0:
                                                    elapsed = time.time() - start_time
                                                    print(f"Logged {valid_count} smooth curves... ({elapsed:.2f}s)", flush=True)
                                                    
                                        except Exception:
                                            continue
                                            
    if batch_data:
        cursor.executemany('''
            INSERT INTO curves (f_poly, h_poly, l_poly, timestamp)
            VALUES (?, ?, ?, ?)
        ''', batch_data)
        conn.commit()
        
    conn.close()
    print(f"Completed F_{64} scan. Total valid smooth curves recorded: {valid_count}", flush=True)

except Exception as e:
    print(">>> AN EXCEPTION OCCURRED:", flush=True)
    traceback.print_exc()
