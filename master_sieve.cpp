#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <NTL/GF2X.h>
#include <NTL/GF2XFactoring.h>
#include <NTL/GF2E.h>
#include <NTL/GF2EX.h>

using namespace std;
using namespace NTL;

// Characteristic 2 Absolute Trace
GF2E field_trace(const GF2E& val, long degree) {
    GF2E tr = val;
    GF2E current = val;
    for(long i = 1; i < degree; ++i) {
        current = sqr(current);
        tr += current;
    }
    return tr;
}

// MATHEMATICAL FILTER
bool is_non_singular(const GF2EX& h, const GF2EX& f) {
    GF2EX dh, df, delta, g;
    diff(dh, h); 
    diff(df, f); 
    delta = sqr(dh) * f + sqr(df);
    GCD(g, h, delta);
    return deg(g) <= 0; 
}

// Point counting bypassing PARI/GMP
long count_points(const GF2EX& h, const GF2EX& f, const vector<GF2E>& eval_domain, long degree) {
    long pts = 1; 
    for (const auto& x : eval_domain) {
        GF2E hx = eval(h, x);
        GF2E fx = eval(f, x);
        if (IsZero(hx)) {
            pts += 1;
        } else {
            GF2E c = fx / sqr(hx);
            if (IsZero(field_trace(c, degree))) pts += 2;
        }
    }
    return pts;
}

void process_field(long k) {
    long q = 1L << k;
    long q2 = 1L << (2 * k);
    
    GF2X P;
    BuildIrred(P, 2 * k);
    GF2E::init(P);
    
    vector<GF2E> Fq2;
    vector<GF2E> Fq;
    
    for (long i = 0; i < q2; ++i) {
        GF2X poly_i;
        for (long b = 0; b < 2 * k; ++b) {
            if ((i >> b) & 1) SetCoeff(poly_i, b, 1);
        }
        GF2E e = conv<GF2E>(poly_i);
        Fq2.push_back(e);
        if (power(e, q) == e) Fq.push_back(e);
    }
    
    // Find a primitive element of the subfield F_q
    GF2E prim;
    if (q == 2) {
        prim = GF2E(1);
    } else {
        for (const auto& e : Fq) {
            if (IsZero(e)) continue;
            long order = 1;
            GF2E temp = e;
            while (temp != GF2E(1)) {
                temp *= e;
                order++;
            }
            if (order == q - 1) {
                prim = e;
                break;
            }
        }
    }

    // Format coefficients as powers of the primitive element
    auto format_coeffs_prim = [&](const vector<GF2E>& coeffs) {
        string s = "\"[";
        for(size_t i = 0; i < coeffs.size(); ++i) {
            if (IsZero(coeffs[i])) {
                s += "-1"; // -1 represents Field Zero
            } else if (q == 2) {
                s += "1";
            } else if (coeffs[i] == GF2E(1)) {
                s += "0";  // prim^0 = 1
            } else {
                long power = 1;
                GF2E temp = prim;
                while (temp != coeffs[i]) {
                    temp *= prim;
                    power++;
                }
                s += to_string(power);
            }
            if (i < coeffs.size() - 1) s += ", ";
        }
        s += "]\"";
        return s;
    };
    
    GF2E gamma;
    for (const auto& e : Fq) {
        if (field_trace(e, k) == GF2E(1)) { gamma = e; break; }
    }
    
    string filename = "gf" + to_string(q) + "_exact_curves.csv";
    ofstream out(filename);
    out << "q,h_coeffs,f_coeffs,target_order,geometric_order,cm_trace_parity\n";
    
    long curves_tested = 0;
    long curves_saved = 0;
    GF2E zero = GF2E(0);
    GF2E one = GF2E(1);
    
    auto evaluate_and_save = [&](vector<GF2E> hc, vector<GF2E> fc) {
        curves_tested++;
        GF2EX h, f;
        for(size_t i=0; i<hc.size(); ++i) SetCoeff(h, i, hc[i]);
        for(size_t i=0; i<fc.size(); ++i) SetCoeff(f, i, fc[i]);
        
        if (!is_non_singular(h, f)) return;
        
        long N1 = count_points(h, f, Fq, k);
        long N2 = count_points(h, f, Fq2, 2 * k);
        
        long a1 = N1 - q - 1;
        long a2 = (N2 - q * q - 1 + a1 * a1) / 2;
        long target_order = 1 + a1 + a2 + q * a1 + q * q;
        long L_minus_1 = 1 - a1 + a2 - q * a1 + q * q;
        long geometric_order = target_order * L_minus_1;
        long trace_parity = (a1 % 2 + 2) % 2; 
        
        out << q << "," << format_coeffs_prim(hc) << "," << format_coeffs_prim(fc) << "," 
            << target_order << "," << geometric_order << "," << trace_parity << "\n";
        curves_saved++;
        
        if (curves_tested % 5000 == 0) cout << "    [PROGRESS] GF(" << q << "): Tested " << curves_tested << " anchors..." << endl;
    };
    
    cout << "\n--- Starting Exact Anchor Generation for GF(" << q << ") ---" << endl;
    
    vector<GF2E> h1 = {zero, one, one};
    for(auto f4 : Fq) for(auto f2 : Fq) for(auto f0 : Fq) evaluate_and_save(h1, {f0, zero, f2, zero, f4, one});
    
    vector<GF2E> h2 = {zero, zero, one};
    for(auto f4 : Fq) for(auto f1 : Fq) for(auto f0 : Fq) evaluate_and_save(h2, {f0, f1, zero, zero, f4, one});
    
    vector<GF2E> h3 = {zero, one, zero};
    for(auto f4 : Fq) for(auto f3 : Fq) for(auto f0 : Fq) {
        evaluate_and_save(h3, {f0, zero, zero, f3, f4, one});
        evaluate_and_save(h3, {f0, zero, gamma, f3, f4, one});
    }
    
    vector<GF2E> h4 = {one, zero, zero};
    for(auto f4 : Fq) for(auto f3 : Fq) for(auto f2 : Fq) evaluate_and_save(h4, {zero, zero, f2, f3, f4, one});
    
    out.close();
    cout << "Completed mapping GF(" << q << "). Tested: " << curves_tested << " | Saved: " << curves_saved << " -> " << filename << endl;
}

int main() {
    vector<long> target_k = {1, 2, 3, 4, 5, 6};
    for(long k : target_k) process_field(k);
    return 0;
}
