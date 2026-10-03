import itertools
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column as Colm, Integer as Intgr, String as Strit, PickleType as PickType
from sqlalchemy.exc import IntegrityError
from sage.all import *

# ==========================================
# DATABASE SCHEMA 
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
# THE WORKER FUNCTION
# ==========================================
def process_branch(i_val):
    db_name = f'sqlite:///GF8_part_{i_val}.db'
    engine = create_engine(db_name)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    F = GF(2**3, name='z4')
    R = PolynomialRing(F, name='x')
    gflist = F.list()
    
    total_processed = 0
    valid_saved = 0
    
    for combo in itertools.product(range(8), repeat=7):
        total_processed += 1
        j, k, l, m_idx, n, p, q = combo
        
        f_poly = R([gflist[m_idx], gflist[l], gflist[k], gflist[j], gflist[i_val], F(1)])
        h_poly = R([gflist[q], gflist[p], gflist[n]])
        
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
            
            if valid_saved % 500 == 0:
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()

    try:
        session.commit()
    except IntegrityError:
        session.rollback()

    return f"Branch i={i_val} finished! Processed {total_processed}, Saved {valid_saved}"
