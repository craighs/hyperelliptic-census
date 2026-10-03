import sqlite3
from sage.all import GF, PolynomialRing, sage_eval, HyperellipticCurve

conn = sqlite3.connect("gf32_curves.db")
cursor = conn.cursor()
cursor.execute("SELECT h_poly, f_poly FROM explicit_curves")
rows = cursor.fetchall()
conn.close()

F = GF(32, 'z')
R = PolynomialRing(F, 'x')
x_sym = R.gen()
z_sym = F.gen()

isogeny_classes = set()

for h_str, f_str in rows:
    h = R(sage_eval(h_str, locals={'x': x_sym, 'z': z_sym}))
    f = R(sage_eval(f_str, locals={'x': x_sym, 'z': z_sym}))
    
    C = HyperellipticCurve(f, h)
    # Use the Jacobian's polynomial or trace coordinates as the canonical invariant in char 2
    J = C.jacobian()
    group_order = J.cardinality()
    
    isogeny_classes.add(group_order)

print(f"Total unique Jacobian group orders (isogeny classes) represented: {len(isogeny_classes)}")
