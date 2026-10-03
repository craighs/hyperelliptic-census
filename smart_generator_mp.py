print("--- Script is starting ---")
import sys

try:
    print("[Debug] Loading libraries...")
    import time
    import itertools
    import multiprocessing
    
    # Force macOS to behave like Linux and use 'fork'
    try:
        multiprocessing.set_start_method('fork', force=True)
    except RuntimeError:
        pass
        
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, declarative_base
    from sqlalchemy import Column, Integer, String, PickleType
    from sage.all import *
    print("[Debug] Libraries loaded successfully!")

    Base = declarative_base()
    class HyperellipticCurveModel(Base):
        __tablename__ = 'hyperelliptic_curves'
        id = Column(Integer, primary_key=True)
        curve_id = Column(String, unique=True, nullable=False)
        isogeny_class = Column(String, index=True, nullable=False)
        f_poly = Column(String)
        h_poly = Column(String)
        jacobian_points = Column(Integer)
        data = Column(PickleType)

    def calculate_jacobian(args):
        f_str, h_str, q, idx = args
        K = GF(q, name='z' if q > 2 else None)
        R = PolynomialRing(K, 'x')
        f = R(f_str)
        h = R(h_str)
        C = HyperellipticCurve(f, h)
        J = C.jacobian()
        curve_pts = int(C.cardinality())
        jacob_pts = int(J.cardinality())
        num_rational = len(C.rational_points())
        return (idx, f_str, h_str, curve_pts, jacob_pts, num_rational, str(factor(jacob_pts)))

    def generate_unique_curves(q):
        print(f"\n" + "="*55)
        print(f" SMART GENERATOR: MP Edition for GF({q})")
        print("="*55)
        t0 = time.time()
        
        K = GF(q, name='z' if q > 2 else None)
        R = PolynomialRing(K, 'x')
        x = R.gen()
        
        print(f"[1/3] Sieving canonical combinations (Optimized Bytearray for RAM)...")
        
        elements = list(K)
        element_lookup = {c: i for i, c in enumerate(elements)}
        add_table = [[element_lookup[a + b] for b in elements] for a in elements]
        
        def poly_key(p, length):
            coeffs = p.list()
            coeffs = coeffs + [K(0)] * (length - len(coeffs))
            return tuple(element_lookup[c] for c in coeffs)

        h_seen = set()
        h_reps = []
        h_stabilizers = {}
        
        uv_params = [(u, v, (u.sqrt())**5) for u in K if u != 0 for v in K]

        for c in itertools.product(K, repeat=3):
            h = c[0]*x**2 + c[1]*x + c[2]
            if h in h_seen: continue
            
            orbit = set()
            for (u, v, w) in uv_params:
                orbit.add(h(u*x + v) / w)
            h_seen.update(orbit)
            
            orbit_list = sorted(list(orbit), key=lambda p: poly_key(p, 3))
            rep = orbit_list[0]
            
            stab = [(u, v, w) for (u, v, w) in uv_params if rep(u*x + v) / w == rep]
            h_reps.append(rep)
            h_stabilizers[rep] = stab
            
        all_P = [c[0]*x**2 + c[1]*x + c[2] for c in itertools.product(K, repeat=3)]
        valid_curves = []
        
        # Pre-compute powers for Base-q fast indexing
        q2, q3, q4, q5 = q**2, q**3, q**4, q**5

        for i, h in enumerate(h_reps):
            V_h_tuples = [poly_key(P**2 + h*P, 5) for P in all_P]
            stab = h_stabilizers[h]
            
            # THE RAM FIX: A 33-Megabyte flat array replacing the Gigabyte Tuple Set
            f_seen = bytearray(q5)
            
            for f_idx in range(q5):
                if f_seen[f_idx]: continue
                
                # Decode 1D integer index back to base-q components
                i0 = f_idx % q
                i1 = (f_idx // q) % q
                i2 = (f_idx // q2) % q
                i3 = (f_idx // q3) % q
                i4 = f_idx // q4
                
                c0, c1, c2, c3, c4 = elements[i0], elements[i1], elements[i2], elements[i3], elements[i4]
                
                f_tail = c4*x**4 + c3*x**3 + c2*x**2 + c1*x + c0
                f = x**5 + f_tail
                df = f.derivative()
                dh = h.derivative()
                S = (dh**2) * f + (df**2)
                
                if h.gcd(S).degree() == 0:
                    valid_curves.append((f, h))
                
                for (u, v, w) in stab:
                    w2 = w**2
                    f_base = f(u*x + v) / w2
                    f_tail_base = f_base - x**5
                    f_tup = poly_key(f_tail_base, 5)
                    
                    for vh_tup in V_h_tuples:
                        # Translate directly back to a 1D index
                        orbit_idx = (
                            add_table[f_tup[0]][vh_tup[0]] +
                            add_table[f_tup[1]][vh_tup[1]] * q +
                            add_table[f_tup[2]][vh_tup[2]] * q2 +
                            add_table[f_tup[3]][vh_tup[3]] * q3 +
                            add_table[f_tup[4]][vh_tup[4]] * q4
                        )
                        f_seen[orbit_idx] = 1
                        
        t1 = time.time()
        print(f"      -> Sieve complete! Found {len(valid_curves)} strictly unique curves.")
        print(f"      -> Sieve Time: {t1-t0:.2f} seconds.")

        print(f"\n[2/3] Distributing Jacobian Calculus across CPU Cores...")
        pool_args = [(str(f), str(h), q, idx) for idx, (f, h) in enumerate(valid_curves)]
        
        num_cores = multiprocessing.cpu_count()
        print(f"      -> Launching {num_cores} workers. (Grab a coffee, this is the heavy part!)")
        
        results = []
        with multiprocessing.Pool(processes=num_cores) as pool:
            for i, res in enumerate(pool.imap_unordered(calculate_jacobian, pool_args), 1):
                results.append(res)
                if i % 1000 == 0 or i == len(valid_curves):
                    print(f"         [Progress: {i} / {len(valid_curves)} curves calculated]")

        print(f"\n[3/3] Saving all results to Unique_GF{q}.db...")
        db_name = f'sqlite:///Unique_GF{q}.db'
        engine = create_engine(db_name)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        for res in results:
            idx, f_str, h_str, curve_pts, jacob_pts, num_rational, factors_str = res
            new_curve = HyperellipticCurveModel(
                curve_id=f"GF{q}_{idx}",
                isogeny_class=f"{curve_pts}_{jacob_pts}",
                f_poly=f_str,
                h_poly=h_str,
                jacobian_points=jacob_pts,
                data=(f_str, h_str, curve_pts, jacob_pts, factors_str, num_rational) 
            )
            session.add(new_curve)
            
        session.commit()
        t2 = time.time()
        print("      -> Database saved successfully!")
        print(f"      -> Total Script Time: {t2-t0:.2f} seconds.")
        print("="*55 + "\n")

    generate_unique_curves(q=32)

except Exception as e:
    print(f"\n!!! CRASHED WITH ERROR: {type(e).__name__} !!!")
    print(e)
    import traceback
    traceback.print_exc()

print("--- Script has finished ---")
