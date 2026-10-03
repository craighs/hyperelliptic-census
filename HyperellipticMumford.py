
# Load the required libraries
# Prime field with 2 elements
F.<z4> = GF(2^3)
R.<x> = PolynomialRing(F)


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

def findQuadraticDivisor(C,f,h,flag):
    K = C.base_ring()
    R.<x> = K[]
    iter  = len(K.list())                     
    β = K.gen()
    #print(β)
    gflist = K.list()
    
    J = C.jacobian()
    card = J.cardinality()
    if flag == 1:
        print("card = ",card," factor(card) = ",factor(card))
    X = J(K)
    mylist=[]
    myerror = []
    #index = 0
    for i in range(iter):
        for j in range(iter):
            for kk in range(iter):
                for l in range(iter):
                    u, v = x^2 + gflist[kk]*x + gflist[l], gflist[j]*x + gflist[i]

                    try:
                        D = X([u,v])
                        p = D.point_of_jacobian_of_curve()
                        po = p.order()
                        
                        if po == card:
                            return 1 #f"Found {(u,v,po)}"
                        if flag == 1:
                            print(po,u,v)
                    #print("i=",i,"j=",j,"k=",k,"l=",l,"u(x)=",u," v(x)=",v," divisor=", X([u,v]))
                        #ll = "i="+str(i)+"j="+str(j)+"k="+str(kk)+"l="+str(l)+" u(x)="+str(u)+" v(x)="+str(v)+" divisor="+str(X([u,v]))," divisor order"+str(po)
                        #mylist.append(ll)
                    except ValueError:
                        myerror.append((i,j,kk,l)) #print() #print(i,j,k,l,u,v,"No")
    return 0 #f"not found"


i,j,k,l,m,n,p,q,f,h,C,J,card,fact, lenc = get_object(str(2)).data
print(C.cardinality())
print(J.cardinality())
print(factor(J.cardinality()))
print(C.rational_points())
mlst = C.rational_points()

len(mlst)
mlst = mlst[1:]


ss = set([])
for qm in range(len(mlst)):
    #print(mlst[qm][0])
    ss.add(mlst[qm][0])
  
print(ss)
print()
for qm in ss:
    dm = J(C.lift_x(qm))
    pp=dm.point_of_jacobian_of_curve()
    print(qm,dm,pp.order())


D = J(C.lift_x(1,all=True)[0])
D1 = J(C.lift_x(z4^2+z4,all=True)[0])
pp=D.point_of_jacobian_of_curve()
ppp = D1.point_of_jacobian_of_curve()
print(D,pp.order())
print(D1,ppp.order())
#pppp = (D*2).point_of_jacobian_of_curve()
#pppp.order()
#D = 2*D


# In[24]:


K = C.base_ring()
R.<x> = K[]
iter  = len(K.list())                     
β = K.gen()
X = J(K)
u,v = x^2 + (z4^2 + z4 + 1)*x + z4^2 + 1, (z4^2 + z4)*x + 1
D = X([u,v])
p = D.point_of_jacobian_of_curve()
p.order()


# In[ ]:


K = C.base_ring()
R.<x> = K[]
iter  = len(K.list())                     
β = K.gen()
X = J(K)
u,v = x^2 + (z4^2 + z4 + 1)*x + z4^2, z4^2*x + 1
#u,v = x^2 + z4^2*x + z4^2, (z4 + 1)*x + 1
D1 = X([u,v])
p = D1.point_of_jacobian_of_curve()
p.order()


# In[ ]:


Set1 = []
for i in range(32):
    for j in range(2):
        #print(i,j,i*D+j*D1)
        Set1.append(i*D+j*D1)
len(set(Set1))        


# In[ ]:


def findQuadraticDivisor(C,f,h,flag):
    K = C.base_ring()
    R.<x> = K[]
    iter  = len(K.list())                     
    β = K.gen()
    #print(β)
    gflist = K.list()
    
    J = C.jacobian()
    card = J.cardinality()
    if flag == 1:
        print("card = ",card," factor(card) = ",factor(card))
    X = J(K)
    mylist=[]
    myerror = []
    #index = 0
    for ii in range(iter):
        for j in range(iter):
            for kk in range(iter):
                for l in range(iter):
                    u, v = x^2 + gflist[kk]*x + gflist[l], gflist[j]*x + gflist[ii]
                    #print(u,v, "j=",j, "ii=",ii)
                    try:
                        D = X([u,v])
                        p = D.point_of_jacobian_of_curve()
                        po = p.order()
                        
                        if po == card:
                            if flag == 1:
                                print("cyclic divisor",po,u,v)                                
                                return 1 #f"Found {(u,v,po)}"
                        if flag == 1:
                            print(po,u,v)
                    #print("i=",i,"j=",j,"k=",k,"l=",l,"u(x)=",u," v(x)=",v," divisor=", X([u,v]))
                        #ll = "i="+str(i)+"j="+str(j)+"k="+str(kk)+"l="+str(l)+" u(x)="+str(u)+" v(x)="+str(v)+" divisor="+str(X([u,v]))," divisor order"+str(po)
                        #mylist.append(ll)
                    except ValueError:
                        myerror.append((ii,j,kk,l)) #print() #print(i,j,k,l,u,v,"No")
    return 0 #f"not found"


# In[ ]:


qqqq = findQuadraticDivisor(C,f,h,1)


# In[ ]:


qqqq


# In[ ]:





# In[ ]:





# In[ ]:


J


# In[ ]:


for i in range(128):
    J = MMList[i].jacobian()
    print(i,MMList[i],"\n",J.cardinality(),"=",factor(J.cardinality())," ",len(MMList[i].rational_points()),"\n",MMList[i].rational_points(),"\n")


# In[ ]:


C=MMList[5]
C.is_singular()
#C.is_smooth()
#C.is_ordinary_singularity?
P=C.defining_polynomial()
f, h = C.hyperelliptic_polynomials()


# In[ ]:


C


# In[ ]:


gcd(x^2+1,diff(x^5+1))


# In[ ]:


(x^2+1)*(diff(x^2+1))


# In[ ]:


gcd(x^8,0)


# In[ ]:


K = C.base_ring()
for y in K:
    print(y)


# In[ ]:


P(K(0),K(1),K(0))


# In[ ]:


P.degree()
s = P(K(1),K(0),K(0))
r = P(K(1),K(1),K(0)) -s
print(s,r)


# In[ ]:


C.points()


# In[ ]:


C.defining_polynomials()


# In[ ]:


C.defining_polynomial()


# In[ ]:


C.rational_points()


# In[ ]:


C.rational_points()


# In[ ]:


XXX = C.rational_points()


# In[ ]:


xxxx=XXX[1]


# In[ ]:


xxxx


# In[ ]:


C.zeta_function()


# In[ ]:


sum(C.frobenius_polynomial())


# In[ ]:


J = C.jacobian();J


# In[ ]:


J.cardinality()


# In[ ]:


get_ipython().run_line_magic('pinfo', 'J.gens_dict')


# In[ ]:


J = J(J.base_ring());J


# In[ ]:


C.lift_x(1,all=True)


# In[ ]:


C.base_scheme()


# In[ ]:


P0 = C.lift_x(1,all=True)[0];P0


# In[ ]:


P1 = C.lift_x(0,all=True)[1];P1


# In[ ]:


Q0 = C.lift_x(z4^2,all=True)[0];Q0


# In[ ]:


#C.lift_x?


# In[ ]:


Q1 = C.lift_x(z4,all=True)[1];Q1


# In[ ]:


R0 = C.lift_x(z4^2 + z4,all=True)[0];R0


# In[ ]:


R1 = C.lift_x(z4^2 + z4,all=True)[1];R1


# In[ ]:


R0m= J(R0);R0m


# In[ ]:


R1m= J(R1);R1m


# In[ ]:


r0 = R0m.point_of_jacobian_of_curve();r0.order()


# In[ ]:


r1 = R1m.point_of_jacobian_of_curve();r1.order()


# In[ ]:


P0m = J(P0);P0m
C.parent_curve()


# In[ ]:


J(K)([x+1,y])


# In[ ]:


P1m = J(P1);P1m


# In[ ]:


Q0m = J(Q0);Q0m


# In[ ]:


Q1m = J(Q1);Q1m


# In[ ]:


p0 = P0m.point_of_jacobian_of_curve();p0.order()


# In[ ]:


p1 = P1m.point_of_jacobian_of_curve();p1.order()


# In[ ]:


q0 = Q0m.point_of_jacobian_of_curve();q0.order()


# In[ ]:


q1 = Q1m.point_of_jacobian_of_curve()


# In[ ]:


q1.order()


# In[ ]:


factor(650)


# In[ ]:


factor(146)


# In[ ]:


LL =[]
for i in range(131):
    LL.append(i*Q0m)
for k in range(131):
    LL.append(k*Q1m)

MM = list(set(LL))
print(len(MM))
#print(MM)
for l in range(27):
    LL.append(l*P1m)
MM = list(set(LL))

for i in range(14):
    LL.append(i*P0m)

for i in range(131):
    LL.append(i*R0m)

for i in range(66):
    LL.append(i*R1m)
MM = list(set(LL))    
print(len(MM))
#for i in range(14):
 #   for j in range(131):
  #      for k in range(131):
   #         for l in range(27):
                #print(i*P0m + j*Q0m)
    #            LL.append(i*P0m + j*Q0m + k*Q1m + l*P1m)
MM = list(set(LL))
#print(MM)
print(len(MM))
#print(MM[0],MM[24])        
print()
#for i in range(625):
 #   for j in range(25):
  #      print(MM[i],"  +  ", MM[j], " = ", MM[i]+MM[j])


# In[ ]:


for i in range(5):
    print(i,i*P1m)


# In[ ]:


for i in range(5):
    print(i,i*Q0m)


# In[ ]:


for i in range(5):
    print(i,i*Q1m)


# In[ ]:


SUm=P0m+Q0m


# In[ ]:


su= SUm.point_of_jacobian_of_curve()


# In[ ]:


su.order()


# In[ ]:


SUm


# In[ ]:


SUm.scheme()


# In[ ]:


Gsu= su.parent()


# In[ ]:


Jsu= Gsu.parent()


# In[ ]:


Jsu


# In[ ]:


Gsu


# In[ ]:


Csu=Jsu.curve()


# In[ ]:


Csu.affine_patch(0)


# In[ ]:


C.affine_patch(0)


# In[ ]:


C.affine_patch(1)


# In[ ]:


C.affine_patch(2)


# In[ ]:


list(P0)


# In[ ]:


P0


# In[ ]:


J.some_elements()


# In[ ]:


P0


# In[ ]:




