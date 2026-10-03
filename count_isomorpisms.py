import sqlite3
from sage.all import GF, PolynomialRing, sage_eval

conn = sqlite3.connect("gf32_curves.db")
cursor = conn.cursor()
cursor.execute("SELECT h_poly, f_poly FROM explicit_curves")
rows = cursor.fetchall()
conn.close()

q = 32
F = GF(q, 'z')
R = PolynomialRing(F, 'x')
x_sym = R.gen()
z_sym = F.gen()

unique_isomorphism_classes = set()

# Precompute all affine transformations x -> a*x + b
affine_transforms = []
for a in F:
    if a == 0:
        continue
    for b in F:
        affine_transforms.append((a, b))

for h_str, f_str in rows:
    h = R(sage_eval(h_str, locals={'x': x_sym, 'z': z_sym}))
    f = R(sage_eval(f_str, locals={'x': x_sym, 'z': z_sym}))
    
    canonical_form = None
    
    # Find the lex-minimal representative under AGL(1, q)
    for a, b in affine_transforms:
        # Substitute x with a*x + b
        # In char 2, y transformation can also be factored, but standard AGL(1,q) 
        # reduction on x bounds the canonical form.
        h_trans = h(a * x_sym + b)
        f_trans = f(a * x_sym + b)
        
        # Create a comparable tuple of coefficients
        sig = (tuple(h_trans.list()), tuple(f_trans.list()))
        
        if canonical_form is None or sig < canonical_form:
            canonical_form = sig
            
    unique_isomorphism_classes.add(canonical_form)

print(f"Exact unique F_32 isomorphism classes: {len(unique_isomorphism_classes)}")
