import sqlite3
import gc
from sage.all import GF, PolynomialRing, HyperellipticCurve

def run_memory_safe_sieve(q, target_a1, target_a2, db_path="verify_explicit_curves.db"):
    """
    Generates verified explicit curves for a specific isogeny class.
    Uses Cartier-Manin trace parity to sieve out 50% of curves instantly,
    then uses Frobenius polynomial to verify exact (a1, a2) invariants.
    """
    F = GF(q, 'z')
    R = PolynomialRing(F, 'x')
    x = R.gen()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS explicit_curves
                      (id INTEGER, q INTEGER, h_poly TEXT, f_poly TEXT, a1 INTEGER, a2 INTEGER)''')
    
    elements = list(F)
    buffer = []
    
    for h2 in elements:
      for h1 in elements:
        for h0 in elements:
          h = h2*x**2 + h1*x + h0
          if h == 0: continue
          
          # Phase 1: Cartier-Manin Sieve (Zero-overhead filter)
          trace_M = h1.trace()
          if trace_M != (target_a1 % 2):
              continue
          
          for f4 in elements:
            for f3 in elements:
              for f2 in elements:
                for f1 in elements:
                  for f0 in elements:
                    f = x**5 + f4*x**4 + f3*x**3 + f2*x**2 + f1*x + f0
                    
                    if (h**2 + 4*f).discriminant() == 0:
                        continue
                        
                    # Phase 2: Exact Point Counting for Isogeny Class Match
                    try:
                        C = HyperellipticCurve(f, h)
                        # Sage returns P(T) = T^4 + c_3*T^3 + c_2*T^2 + c_1*T + c_0
                        # For characteristic 2, our invariants map to the coefficients.
                        # N = P(1) is the geometric order.
                        frob = C.frobenius_polynomial()
                        poly_coeffs = frob.list()
                        
                        curve_a1 = poly_coeffs[3]
                        curve_a2 = poly_coeffs[2]
                        
                        if curve_a1 == target_a1 and curve_a2 == target_a2:
                            buffer.append((1, q, str(h), str(f), int(curve_a1), int(curve_a2)))
                            
                            if len(buffer) >= 1000:
                                cursor.executemany('''
                                    INSERT INTO explicit_curves (id, q, h_poly, f_poly, a1, a2)
                                    VALUES (?, ?, ?, ?, ?, ?)''', buffer)
                                conn.commit()
                                buffer = []
                                gc.collect()
                    except Exception:
                        pass
                        
    if buffer:
        cursor.executemany('''
            INSERT INTO explicit_curves (id, q, h_poly, f_poly, a1, a2)
            VALUES (?, ?, ?, ?, ?, ?)''', buffer)
        conn.commit()
    conn.close()
    print(f"Finished search for q={q}, a1={target_a1}, a2={target_a2}")

if __name__ == "__main__":
    # Let's test a known valid isogeny class in F_2.
    # From the bounds: let's pick a valid target from your gf_master.db for q=2
    # You can change these a1, a2 values to match any known target in your master DB.
    run_memory_safe_sieve(q=2, target_a1=1, target_a2=2, db_path="verify_gf2_explicit.db")
