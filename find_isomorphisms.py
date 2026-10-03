from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
from collections import defaultdict
from sage.all import *

Base = declarative_base()
class HyperellipticCurveModel(Base):
    __tablename__ = 'hyperelliptic_curves'
    id = Column(Integer, primary_key=True)
    curve_id = Column(String)
    isogeny_class = Column(String)
    f_poly = Column(String)
    h_poly = Column(String)

engine = create_engine('sqlite:///GF2c.db')
Session = sessionmaker(bind=engine)
session = Session()

# 1. Custom Isomorphism Checker strictly for Genus 2, Characteristic 2
def are_isomorphic_char2(f1_str, h1_str, f2_str, h2_str):
    K = GF(2)
    R = PolynomialRing(K, 'x')
    x = R.gen()
    
    # Parse the strings back into Sage Math polynomials
    f1 = R(f1_str)
    h1 = R(h1_str)
    f2 = R(f2_str)
    h2 = R(h2_str)
    
    # The 6 valid Moebius transformations in GF(2)
    matrices = [
        (K(1), K(0), K(0), K(1)), # x
        (K(1), K(1), K(0), K(1)), # x + 1
        (K(0), K(1), K(1), K(0)), # 1 / x
        (K(0), K(1), K(1), K(1)), # 1 / (x+1)
        (K(1), K(0), K(1), K(1)), # x / (x+1)
        (K(1), K(1), K(1), K(0))  # (x+1) / x
    ]
    
    # The 16 valid P(X) polynomials of degree <= 3 in GF(2)
    Ps = [R([c0, c1, c2, c3]) for c0 in K for c1 in K for c2 in K for c3 in K]
    
    for (a,b,c,d) in matrices:
        # Transform H(X) = (cx+d)^3 * h1((ax+b)/(cx+d))
        H_X = R(0)
        for i, coeff in enumerate(h1.list()):
            H_X += K(coeff) * (a*x + b)**i * (c*x + d)**(3 - i)
            
        # If the H polynomials don't match after substitution, it's not a match!
        if H_X != h2:
            continue
            
        # Transform F(X) = (cx+d)^6 * f1((ax+b)/(cx+d))
        F_part = R(0)
        for i, coeff in enumerate(f1.list()):
            F_part += K(coeff) * (a*x + b)**i * (c*x + d)**(6 - i)
            
        # Add the Y-shift: F_new = F_part + P(X)^2 + H_X * P(X)
        for P in Ps:
            F_X = F_part + P**2 + H_X * P
            if F_X == f2:
                return True # We found the exact disguise!
                
    return False

# 2. Group curves by Isogeny Class
curves_by_isogeny = defaultdict(list)
for row in session.query(HyperellipticCurveModel).all():
    curves_by_isogeny[row.isogeny_class].append({
        'id': row.curve_id,
        'f_poly': row.f_poly,
        'h_poly': row.h_poly
    })

total_isomorphism_classes = 0

print("Analyzing GF(2) Curves for Isomorphisms (Custom Char 2 Engine)...")
print("=" * 60)

for iso_class, curves in curves_by_isogeny.items():
    print(f"\nIsogeny Class {iso_class} (Contains {len(curves)} total equations)")
    
    isomorphism_buckets = []
    
    for c_dict in curves:
        placed = False
        for bucket in isomorphism_buckets:
            ref = bucket[0]
            # Test it against our custom engine
            if are_isomorphic_char2(c_dict['f_poly'], c_dict['h_poly'], ref['f_poly'], ref['h_poly']):
                bucket.append(c_dict)
                placed = True
                break
        
        if not placed:
            isomorphism_buckets.append([c_dict])
            total_isomorphism_classes += 1

    for idx, bucket in enumerate(isomorphism_buckets):
        print(f"  -> Isomorphism Group {idx + 1}: {len(bucket)} curve(s) are identical copies.")

print("=" * 60)
print(f"Total unique geometric curves (Isomorphism Classes) found: {total_isomorphism_classes}")
