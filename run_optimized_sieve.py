import sqlite3
import os
import time
import scipy.stats.qmc as qmc
from sage.all import *

db_name = "gf64_curves.db"
q_val = 64

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

cursor.execute("""
    SELECT c.id, c.group_order 
    FROM curves c
    LEFT JOIN explicit_curves e ON c.id = e.id
    WHERE e.id IS NULL AND c.group_order IS NOT NULL
""")
missing_rows = cursor.fetchall()
missing_dict = {str(row[1]).strip(): row[0] for row in missing_rows}
print(f"Loaded {len(missing_dict)} target group orders.")

F = GF(q_val, 'z')
R = PolynomialRing(F, 'x')
F_elements = [F(0)] + [F('z') ** i for i in range(q_val - 1)]

sobol = qmc.Sobol(d=8, scramble=True)
batch_size = 4096
found = 0
tested = 0
start_time = time.time()

while len(missing_dict) > 0:
    raw_samples = sobol.random(n=batch_size)
    int_indices = (raw_samples * 64).astype(int)

    for indices in int_indices:
        if len(missing_dict) == 0:
            break
        tested += 1

        h0, h1, h2, f0, f1, f2, f3, f4 = [F_elements[i] for i in indices]
        h = h2 * R('x')**2 + h1 * R('x') + h0
        f = R('x')**5 + f4 * R('x')**4 + f3 * R('x')**3 + f2 * R('x')**2 + f1 * R('x') + f0

        # Quick discriminant / smoothness pre-check
        if f.discriminant() == 0:
            continue

        try:
            C = HyperellipticCurve(f, h)
            N1 = int(C.count_points(1)[0])
            N2 = int(C.count_points(2)[0])

            a1 = q_val + 1 - N1
            a2 = (N2 - q_val**2 - 1 + a1**2) // 2
            N = 1 + (q_val + 1) * a1 + a2 + q_val**2
            group_str = str(N)
        except Exception:
            continue

        if group_str in missing_dict:
            row_id = missing_dict.pop(group_str)
            J = C.jacobian()

            prime_factors = list(factor(N))
            max_p_orders = {p: 0 for p, _ in prime_factors}
            for _ in range(30):
                try:
                    D = J.random_element()
                    for p, v in prime_factors:
                        if max_p_orders[p] == v: continue
                        cofactor = N // (p**v)
                        Dp = cofactor * D
                        p_ord = 0
                        while Dp != J(0) and p_ord <= v:
                            Dp = p * Dp
                            p_ord += 1
                        if p_ord > max_p_orders[p]: max_p_orders[p] = p_ord
                except Exception:
                    continue

            p_partitions = {}
            for p, v in prime_factors:
                e = max_p_orders[p]
                if e == v: p_partitions[p] = [e]
                elif e == v - 1: p_partitions[p] = [e, 1]
                else: p_partitions[p] = [e, v - e]

            max_rank = max((len(part) for part in p_partitions.values()), default=0)
            if max_rank == 0: invariants = [N]
            else:
                invariants = [1] * max_rank
                for p, part in p_partitions.items():
                    for i, exp in enumerate(part): invariants[i] *= (int(p)**exp)
                invariants = sorted([inv for inv in invariants if inv > 1])

            cursor.execute(
                "INSERT OR REPLACE INTO explicit_curves (id, h_poly, f_poly, invariant_factors) VALUES (?, ?, ?, ?)",
                (row_id, str(h), str(f), str(invariants))
            )
            conn.commit()
            found += 1
            print(f"Matched! Total found: {found} | Group Order: {N}")

    if tested % 5000 == 0:
        print(f"Tested: {tested} | Remaining targets: {len(missing_dict)} | Elapsed: {time.time() - start_time:.1f}s")

conn.close()
print("Sieve complete.")
