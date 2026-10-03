from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column as Colm, Integer as Intgr, String as Strit, PickleType as PickType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# Configure the database
DATABASE_URL = 'sqlite:///hyperellipticGF8b.db'  # Use SQLite for persistence
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class SageObject(Base):
    __tablename__ = 'sage_objects'

    id = Colm(Intgr, primary_key=True)
    name = Colm(Strit, nullable=False)
    data = Colm(PickType)  # This will allow storing SageMath objects

# Create the database table
Base.metadata.create_all(engine)

def add_object(name, sage_object):
    new_object = SageObject(name=name, data=sage_object)
    session.add(new_object)
    session.commit()

def get_object(object_id):
    sage_object = session.query(SageObject).filter(SageObject.id == object_id).first()
    return sage_object

def update_object(object_id, new_name, new_data):
    sage_object = get_object(object_id)
    if sage_object:
        sage_object.name = new_name
        sage_object.data = new_data
        session.commit()

def delete_object(object_id):
    sage_object = get_object(object_id)
    if sage_object:
        session.delete(sage_object)
        session.commit()

# Load the required libraries
# Prime field with 2 elements
F.<z4> = GF(2^5)
R.<x> = PolynomialRing(F)
gflist = F.list()
sizeit = len(gflist)
#P.<x> = GF(8,'a')[]
#C = HyperellipticCurve(x^7 + 1, a)
#MMList = []
lst = []
with open('8.txt','r') as f:
    for line in f:
        i,j,k,l,m,n,p,q = line.strip().split(' ')
        i = eval(i)
        j = eval(j)
        k = eval(k)
        l = eval(l)
        m = eval(m)
        n = eval(n)
        p = eval(p)
        q = eval(q)
        f = x^5+ gflist[i]*x^4+gflist[j]*x^3+ gflist[k]*x^2 + gflist[l]*x + gflist[m]
        h = gflist[n]*x^2+ gflist[p]*x + gflist[q]
 
        try:
            C = HyperellipticCurve(f,h)
            J = C.jacobian()
            newtuple = (C.cardinality(),J.cardinality())
                                            #print(newtuple)
            if newtuple in lst:
                t = 0
            else:    
                lst.append(newtuple)
                                       #sage_var = C
                sage_var = (i,j,k,l,m,n,p,q,f,h,C,J,J.cardinality(),factor(J.cardinality()),len(C.rational_points()))
                add_object("HyperellipticCurve", sage_var)  # Save to database
        except:
              t = 0 #print(i,j,k,l,m,n,p,q)
        finally:
              t = 0

                            
