import sqlite3
import time

def generate_gf256_db():
    db_name = "gf256_curves.db"
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

    q = 256
    sqrt_q = 16.0
    valid_count = 0
    batch_data = []

    # Weil bounds for genus 2 over F_256: |a1| <= 4 * sqrt(256) = 64
    for a1 in range(-64, 65):
        for a2 in range(-400, 1000):
            if abs(a1) <= 64 and -2*q - a1*a1//4 <= a2 <= 2*q + 65*q:
                # Group order evaluated at T = 1: L(1) = 1 - a1 + a2 - q*a1 + q^2
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
    print(f"Generated {valid_count} records in {db_name}")

if __name__ == "__main__":
    generate_gf256_db()
