from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
from sage.all import *

# 1. Connect to the database (Example: GF8)
Base = declarative_base()
class HyperellipticCurveModel(Base):
    __tablename__ = 'hyperelliptic_curves'
    id = Column(Integer, primary_key=True)
    f_poly = Column(String)
    h_poly = Column(String)

engine = create_engine('sqlite:///Unique_GF8.db')
Session = sessionmaker(bind=engine)
session = Session()

# 2. Fetch a specific curve
record = session.query(HyperellipticCurveModel).first()

# 3. Rebuild the Math Environment
q = 8
K = GF(q, name='z' if q > 2 else None)
R = PolynomialRing(K, 'x')

# 4. Bring the curve back to life!
f = R(record.f_poly)
h = R(record.h_poly)
C = HyperellipticCurve(f, h)
J = C.jacobian()

print(f"Successfully loaded curve: {C}")
