#include <iostream>
#include <NTL/GF2X.h>
#include <NTL/GF2XFactoring.h>
#include <NTL/GF2E.h>
#include <NTL/GF2EX.h>

using namespace std;
using namespace NTL;

// Fast point counting for y^2 + h(x)y = f(x) over GF(2^k)
long count_points(const GF2EX& h, const GF2EX& f, long k) {
    long num_points = 1; // Start with 1 for the point at infinity
    long q = 1L << k;    // q = 2^k

    for (long i = 0; i < q; ++i) {
        // 1. Build the field element 'x' from integer 'i'
        GF2X poly_i;
        for (long bit = 0; bit < k; ++bit) {
            if ((i >> bit) & 1) {
                SetCoeff(poly_i, bit, 1);
            }
        }
        GF2E x = conv<GF2E>(poly_i);

        // 2. Evaluate h(x) and f(x)
        GF2E hx = eval(h, x);
        GF2E fx = eval(f, x);

        // 3. Artin-Schreier evaluation
        if (IsZero(hx)) {
            // If h(x) == 0, there is exactly 1 square root in char 2
            num_points += 1;
        } else {
            // If h(x) != 0, equation becomes z^2 + z = c
            GF2E hx_sq = hx * hx;
            GF2E c = fx / hx_sq;
            
            // If trace is 0, there are 2 solutions. If 1, there are 0.
            if (trace(c) == 0) {
                num_points += 2;
            }
        }
    }
    return num_points;
}

int main() {
    long k = 4; // We are testing GF(16)
    
    // Initialize the finite field GF(2^k)
    GF2X P;
    BuildIrred(P, k); // NTL finds an irreducible polynomial of degree 4
    GF2E::init(P);    // Initializes the GF2E context

    cout << "Initialized GF(16) successfully." << endl;

    // Define polynomials: h(x) = x^2 + x, f(x) = x^5 + x^3 + 1
    GF2EX h, f;
    
    // Set h(x) coefficients
    SetCoeff(h, 2, GF2E(1));
    SetCoeff(h, 1, GF2E(1));
    
    // Set f(x) coefficients
    SetCoeff(f, 5, GF2E(1));
    SetCoeff(f, 3, GF2E(1));
    SetCoeff(f, 0, GF2E(1));

    // Count the points
    long N1 = count_points(h, f, k);
    cout << "Number of points on curve over GF(16): " << N1 << endl;

    return 0;
}
