from sage.all import *

print("Setting up F_64...")
F = GF(64, 'z')
R = PolynomialRing(F, 'x')

# Hardcode a known non-singular genus 2 curve shape
h = R('x^2 + x')
f = R('x^5 + x^3 + 1')

print("Constructing curve...")
C = HyperellipticCurve(f, h)
print(f"Curve Genus: {C.genus()}")

print("Attempting frobpoly()...")
L = C.frobpoly()
print(f"Frobenius polynomial: {L}")

print("Extracting coefficients...")
a1 = -int(L[3])
a2 = int(L[2])
print(f"a1: {a1}, a2: {a2}")
