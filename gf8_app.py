import itertools
import multiprocessing as mp
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column as Colm, Integer as Intgr, String as Strit, PickleType as PickType
from sqlalchemy.exc import IntegrityError

# This will work perfectly when run via `sage -python`
from sage.all import *

# ==========================================
# 1. DATABASE SCHEMA (No specific file bound yet)
# ==========================================
Base = declarative_base()

class HyperellipticCurveModel(Base):
    __tablename__ = 'hyperelliptic_curves'
    id = Colm(Intgr, primary_key=True)
    curve_id = Colm(Strit, unique=True, nullable=False)
    isogeny_class = Colm(Strit, index=True, nullable=False)
    f_poly = Colm(Strit)
    h_poly = Colm(Strit)
    jacobian_points = Colm(Intgr)
    data = Colm(PickType)

# ==========================================
# 2. THE WORKER FUNCTION (Runs on a single CPU core)
# ==========================================
def process_branch(i_val):
    """
    Processes all 2,097,152 combinations for a specific starting coefficient 'i_val'.
    Writes to an isolated database (e.g., GF8_part_0.db) to prevent locking errors.
    """
    db_name = f'sqlite:///GF8_part_{i_val}.db'
    engine = create_engine(db_name)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Initialize Field purely internally per-process
    F = GF(2**3, name='z4')
    R = PolynomialRing(F, name='x')
    gflist = F.list()
    
    total_processed = 0
    valid_saved = 0
    
    # Generate the remaining 7 coefficients (0 through 7)
    for combo in itertools.product(range(8), repeat=7):
        total_processed += 1
        j, k, l, m_idx, n, p, q = combo
        
        # Fast polynomial construction via lists
        f_poly = R([gflist[m_idx], gflist[l], gflist[k], gflist[j], gflist[i_val], F(1)])
        h_poly = R([gflist[q], gflist[p], gflist[n]])
        
        # --- FAST SINGULARITY FILTER ---
        if h_poly.is_zero():
            continue
            
        df = f_poly.derivative()
        dh = h_poly.derivative()
        S = (dh**2) * f_poly + (df**2)
        
        if h_poly.gcd(S).degree() == 0:
            C = HyperellipticCurve(f_poly, h_poly)
            J = C.jacobian()
            
            curve_pts = int(C.cardinality())
            jacob_pts = int(J.cardinality())
            
            curve_id = f"{i_val}_{j}_{k}_{l}_{m_idx}_{n}_{p}_{q}"
            isogeny_class = f"{curve_pts}_{jacob_pts}"
            
            sage_tuple = (
                i_val, j, k, l, m_idx, n, p, q, 
                C, J, factor(jacob_pts), len(C.rational_points())
            )
            
            new_curve = HyperellipticCurveModel(
                curve_id=curve_id,
                isogeny_class=isogeny_class,
                f_poly=str(f_poly),
                h_poly=str(h_poly),
                jacobian_points=jacob_pts,
                data=sage_tuple
            )
            
            session.add(new_curve)
            valid_saved += 1
            
            # Batch commit every 500 valid curves
            if valid_saved % 500 == 0:
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()

    # Final commit for the remaining curves in the queue
    try:
        session.commit()
    except IntegrityError:
        session.rollback()

    return f"Branch i={i_val} finished! Processed {total_processed}, Saved {valid_saved}"

# ==========================================
# 3. THE MULTIPROCESSING MANAGER
# ==========================================
if __name__ == '__main__':
    print("Starting Multiprocessing Exhaustive Search for GF(8)...")
    print("Splitting 16.7 million combinations across 4 CPUs.")
    
    # Generate the 8 starting branches (i = 0 through 7)
    branches = list(range(8))
    
    # Launch a pool of 4 workers
    with mp.Pool(processes=4) as pool:
        results = pool.map(process_branch, branches)
        
    print("\n" + "="*40)
    print("ALL PROCESSES COMPLETE!")
    for res in results:
        print(res)
