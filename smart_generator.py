import time
import itertools
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, PickleType
from sage.all import *

# ==========================================
# DATABASE SETUP
# ==========================================
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

# ==========================================
# ORBIT-STABILIZER SIEVE ENGINE
# ==========================================
def generate_unique_curves(q):
    print(f"\n" + "="*55)
    print(f" SMART GENERATOR: Unique Genus 2 Curves for GF({q})")
    print("="*55)
    t0 = time.time()
    
    K = GF(q, name='z' if q > 2 else None)
    R = PolynomialRing(K, 'x')
    x = R.gen()
    
    print("[1/3] Finding canonical h(x) templates...")
    h_seen = set()
    h_reps = []
    h_stabilizers = {}
    
    # Pre-calculate (u, v, w) transformations where w = u^(5/2)
    uv_params = []
    for u in K:
        if u == 0: continue
        w = (u.sqrt())**5
        for v in K:
            uv_params.append((u, v, w))
            
    def poly_key(p, length):
        coeffs = p.list()
        coeffs = coeffs + [K(0)] * (length - len(coeffs))
        return tuple(c.integer_representation() for c in coeffs)

    # Find the unique base shapes for h(x)
    for c in itertools.product(K, repeat=3):
        h = c[0]*x**2 + c[1]*x + c[2]
        if h in h_seen: continue
        
        orbit = set()
        for (u, v, w) in uv_params:
            orbit.add(h(u*x + v) / w)
        h_seen.update(orbit)
        
        # Pick the mathematically simplest version as our representative template
        orbit_list = sorted(list(orbit), key=lambda p: poly_key(p, 3))
        rep = orbit_list[0]
        
        # Track which transformations leave this template unchanged
        stab = [(u, v, w) for (u, v, w) in uv_params if rep(u*x + v) / w == rep]
        h_reps.append(rep)
        h_stabilizers[rep] = stab
        
    print(f"      -> Found {len(h_reps)} canonical h(x) templates.")
    
    print("\n[2/3] Sieving billions of combinations into unique f(x) shapes...")
    all_P = [c[0]*x**2 + c[1]*x + c[2] for c in itertools.product(K, repeat=3)]
    
    valid_curves = []
    
    for i, h in enumerate(h_reps):
        V_h = [P**2 + h*P for P in all_P]
        stab = h_stabilizers[h]
        f_seen = set()
        
        for c in itertools.product(K, repeat=5):
            f_tail = c[0]*x**4 + c[1]*x**3 + c[2]*x**2 + c[3]*x + c[4]
            f_key = poly_key(f_tail, 5)
            
            if f_key in f_seen:
                continue
                
            f = x**5 + f_tail
            
            # Check non-singularity. If singular, the whole orbit is singular!
            df = f.derivative()
            dh = h.derivative()
            S = (dh**2) * f + (df**2)
            is_valid = (h.gcd(S).degree() == 0)
            
            if is_valid:
                valid_curves.append((f, h))
            
            # Map out all disguised copies and mark them as 'seen' so we skip them
            for (u, v, w) in stab:
                w2 = w**2
                f_base = f(u*x + v) / w2
                f_tail_base = f_base - x**5
                for vh in V_h:
                    orbit_poly = f_tail_base + vh
                    f_seen.add(poly_key(orbit_poly, 5))
                    
    t1 = time.time()
    print(f"      -> Sieve complete! Down to {len(valid_curves)} strictly unique geometric curves.")
    print(f"      -> Math Engine Time: {t1-t0:.3f} seconds.")

    print(f"\n[3/3] Calculating Jacobians and saving to Unique_GF{q}.db...")
    db_name = f'sqlite:///Unique_GF{q}.db'
    engine = create_engine(db_name)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    for idx, (f, h) in enumerate(valid_curves):
        C = HyperellipticCurve(f, h)
        J = C.jacobian()
        
        curve_pts = int(C.cardinality())
        jacob_pts = int(J.cardinality())
        
        new_curve = HyperellipticCurveModel(
            curve_id=f"GF{q}_{idx}",
            isogeny_class=f"{curve_pts}_{jacob_pts}",
            f_poly=str(f),
            h_poly=str(h),
            jacobian_points=jacob_pts,
            data=(f, h, C, J, factor(jacob_pts), len(C.rational_points()))
        )
        session.add(new_curve)
        
    session.commit()
    print("      -> Database saved successfully!")
    print("="*55 + "\n")

if __name__ == '__main__':
    # You can change this number to 4, 8, or 16!
    generate_unique_curves(q=2)
