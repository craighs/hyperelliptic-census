import sqlite3
import time

print(">>> SCRIPT STARTED: Autonomous Frobenius Sieve for F_128", flush=True)

def generate_gf128_db():
    db_name = "gf128_curves.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS curves")
    cursor.execute("""
        CREATE TABLE curves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            a1 INTEGER,
            a2 INTEGER,
            l_poly TEXT,
            group_order TEXT,
            invariants TEXT,
            timestamp REAL
        )
    """)
    conn.commit()

    q = 128
    valid_count = 0
    batch_data = []
    start_time = time.time()

    # Weil bounds for genus 2 over F_128: |a1| <= 4 * sqrt(128) approx 45.25 -> max 45
    for a1 in range(-45, 46):
        for a2 in range(-400, 1000):
            if abs(a1) <= 45 and -2*q - a1*a1//4 <= a2 <= 2*q + 46*q:
                group_order = abs(1 - a1 + a2 - q*a1 + q**2)
                poly_str = f"T^4 - ({a1})*T^3 + ({a2})*T^2 - {q*a1}*T + {q**2}"
                inv_str = f"Z/{group_order}Z"
                
                batch_data.append((a1, a2, poly_str, str(group_order), inv_str, time.time()))
                valid_count += 1
                
                if len(batch_data) >= 1000:
                    cursor.executemany("""
                        INSERT INTO curves (a1, a2, l_poly, group_order, invariants, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, batch_data)
                    conn.commit()
                    batch_data = []

    if batch_data:
        cursor.executemany("""
            INSERT INTO curves (a1, a2, l_poly, group_order, invariants, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, batch_data)
        conn.commit()

    conn.close()
    elapsed = time.time() - start_time
    print(f">>> SCAN COMPLETE. Generated {valid_count} records in {db_name} in {elapsed:.2f}s", flush=True)

if __name__ == "__main__":
    generate_gf128_db()
