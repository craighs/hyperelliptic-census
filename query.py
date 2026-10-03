from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String

# 1. Minimal setup just to read the database
Base = declarative_base()

class HyperellipticCurveModel(Base):
    __tablename__ = 'hyperelliptic_curves'
    id = Column(Integer, primary_key=True)
    curve_id = Column(String)
    isogeny_class = Column(String)
    f_poly = Column(String)
    h_poly = Column(String)

# Connect to the database we just built
engine = create_engine('sqlite:///GF2c.db')
Session = sessionmaker(bind=engine)
session = Session()

# 2. Query the isogeny classes and group them
print("Isogeny Class Summary (GF(2)):")
print("-" * 55)

# This runs a native SQL GROUP BY query, which is lightning fast
results = session.query(
    HyperellipticCurveModel.isogeny_class, 
    func.count(HyperellipticCurveModel.id)
).group_by(
    HyperellipticCurveModel.isogeny_class
).order_by(
    func.count(HyperellipticCurveModel.id).desc()
).all()

# 3. Print the results nicely
for isogeny_class, count in results:
    # Split our combined string back into curve points and jacobian points
    c_pts, j_pts = isogeny_class.split('_')
    
    print(f"Curve Points: {c_pts:>2} | Jacobian Points: {j_pts:>2} | Total Curves: {count}")

print("-" * 55)
print(f"Total unique isogeny classes found: {len(results)}")
