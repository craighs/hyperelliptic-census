import sqlite3
import time
import multiprocessing as mp
from queue import Empty
from sage.all import *

def setup_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS curve_instances (
            instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            weil_id INTEGER,
            h_poly TEXT,
            f_poly TEXT,
            a1 INTEGER,
            a2 INTEGER,
            timestamp REAL,
            FOREIGN KEY(weil_id) REFERENCES curves(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_instance_weil_id ON curve_instances(weil_id)")
    conn.commit()
    return conn

def worker_task(worker_id, weil_map, queue, stop_event):
    # Initialize the field and ring locally in the worker memory space
    F = GF(64, 'z')
    R = PolynomialRing(F, 'x')
    
    while not stop_event.is_set():
        h = R.random_element(degree=2)
        f = R.random_element(degree=5)
        
        if f.degree() != 5:
            continue
            
        try:
            C = HyperellipticCurve(f, h)
            if C.genus() != 2:
                continue
            
            # The heavy lifting: compute Frobenius trace bounds
            L = C.frobpoly()
            a1 = -int(L[3])
            a2 = int(L[2])
            
            # If the Weil coefficients map to an abstract curve in our DB, send to listener
            if (a1, a2) in weil_map:
                target_weil_id = weil_map[(a1, a2)]
                queue.put((target_weil_id, str(h), str(f), a1, a2))
                
        except ValueError:
            continue
        except Exception:
            continue

def listener_task(db_name, queue, stop_event):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    F = GF(64, 'z')
    R = PolynomialRing(F, 'x')
    
    # Preload known curve isomorphisms into memory for rapid deduplication
    known_isomorphisms = {}
    cursor.execute("SELECT weil_id, h_poly, f_poly FROM curve_instances")
    
    for wid, h_str, f_str in cursor.fetchall():
        try:
            h_poly = R(h_str)
            f_poly = R(f_str)
            C_known = HyperellipticCurve(f_poly, h_poly)
            if wid not in known_isomorphisms:
                known_isomorphisms[wid] = []
            known_isomorphisms[wid].append(C_known)
        except Exception:
            continue
            
    total_known = sum(len(v) for v in known_isomorphisms.values())
    print(f"[Listener] Reconstructed {total_known} known isomorphism classes from database.", flush=True)
    
    new_found = 0
    start_time = time.time()
    
    while True:
        try:
            # timeout=1.0 allows the loop to regularly check if stop_event is triggered
            item = queue.get(timeout=1.0)
            if item == "SHUTDOWN":
                break
                
            target_weil_id, h_str, f_str, a1, a2 = item
            
            # Reconstruct the candidate curve from the worker's strings
            h_poly = R(h_str)
            f_poly = R(f_str)
            C = HyperellipticCurve(f_poly, h_poly)
            
            # Deduplication Check
            is_new_class = True
            if target_weil_id in known_isomorphisms:
                for C_existing in known_isomorphisms[target_weil_id]:
                    if C.is_isomorphic(C_existing):
                        is_new_class = False
                        break
                        
            if is_new_class:
                cursor.execute("""
                    INSERT INTO curve_instances (weil_id, h_poly, f_poly, a1, a2, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (target_weil_id, h_str, f_str, a1, a2, time.time()))
                conn.commit()
                
                if target_weil_id not in known_isomorphisms:
                    known_isomorphisms[target_weil_id] = []
                known_isomorphisms[target_weil_id].append(C)
                
                new_found += 1
                total_known += 1
                
                elapsed = time.time() - start_time
                print(f"[Listener] NEW isomorphism class cataloged! Weil ID: {target_weil_id} (a1={a1}, a2={a2}). Total cataloged: {total_known} ({elapsed:.1f}s)", flush=True)
                
        except Empty:
            if stop_event.is_set():
                break
        except Exception:
            continue
            
    conn.close()
    print(f"\n[Listener] Shutting down. Cataloged {new_found} new unique classes this session.")

def run_multicore_sieve():
    print(">>> SCRIPT STARTED: Multi-Core Isomorphism Sieve for F_64", flush=True)
    db_name = "gf64_curves.db"
    
    # Initialize DB and pull the Weil map
    conn = setup_database(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT id, a1, a2 FROM curves")
    weil_map = {(row[1], row[2]): row[0] for row in cursor.fetchall()}
    conn.close()
    
    print(f"Loaded {len(weil_map)} Weil abstract targets.")
    
    # Setup IPC (Inter-Process Communication)
    manager = mp.Manager()
    queue = manager.Queue()
    stop_event = manager.Event()
    
    num_workers = 4
    print(f">>> Spawning 1 Listener Process and {num_workers} Worker Processes...", flush=True)
    
    # Spin up Listener
    listener = mp.Process(target=listener_task, args=(db_name, queue, stop_event))
    listener.start()
    
    # Spin up 4 independent Workers
    workers = []
    for i in range(num_workers):
        p = mp.Process(target=worker_task, args=(i, weil_map, queue, stop_event))
        p.start()
        workers.append(p)
        
    print(">>> Sieve is actively burning across 4 cores. Press CTRL+C at any time to gracefully halt.", flush=True)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n>>> CTRL+C received. Sending halt signal to all cores...")
        stop_event.set()
        
        # Wait for workers to finish their current loop
        for w in workers:
            w.join()
            
        # Send shutdown pill to listener
        queue.put("SHUTDOWN")
        listener.join()
        print(">>> All processes cleanly terminated.")

if __name__ == '__main__':
    run_multicore_sieve()
