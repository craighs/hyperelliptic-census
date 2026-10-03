{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "a = -17/37\n            sage: copy(a) is a\n            True\n\n        Coercion does not make a new copy::\n\n            sage: QQ(a) is a\n            True\n\n        Calling the constructor directly makes a new copy::\n\n            sage: Rational(a) is a\n            False\n        \");"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "a = -2/3\n        sage: type(a)\n        <class 'sage.rings.rational.Rational'>\n        sage: parent(a)\n        Rational Field\n        sage: Rational('1/0')\n        Traceback (most recent call last):\n        ...\n        TypeError: unable to convert '1/0' to a rational\n        sage: Rational(1.5)\n        3/2\n        sage: Rational('9/6')\n        3/2\n        sage: Rational((2^99,2^100))\n        1/2\n        sage: Rational((\\"2\\", \\"10\\"), 16)\n        1/8\n        sage: Rational(QQbar(125/8).nth_root(3))                                        # needs sage.rings.number_field\n        5/2\n        sage: Rational(AA(209735/343 - 17910/49*golden_ratio).nth_root(3)               # needs sage.rings.number_field sage.symbolic\n\n",
    "          + 3*AA(golden_ratio))\n        53/7\n        sage: QQ(float(1.5))\n        3/2\n        sage: QQ(RDF(1.2))\n        6/5\n\n    Conversion from fractions::\n\n        sage: import fractions\n        sage: f = fractions.Fraction(1r, 2r)\n        sage: Rational(f)\n        1/2\n\n    Conversion from PARI::\n\n        sage: Rational(pari('-939082/3992923'))                                         # needs sage.libs.pari\n        -939082/3992923\n        sage: Rational(pari('Pol([-1/2])'))  #9595                                      # needs sage.libs.pari\n        -1/2\n\n    Conversions from numpy::\n\n        sage: # needs numpy\n        sage: import numpy as np\n        sage: QQ(np.int8('-15'))\n        -15\n        sage: QQ(np.int16('-32'))\n        -32\n        sage: QQ(np.int32('-19'))\n        -19\n        sage: QQ(np.uint32('1412'))\n        1412\n\n        sage: QQ(np.float16('12'))                                                      # needs numpy\n        12\n\n    Conversions from gmpy2::\n\n      \"\"  sage: from gmpy2 import *\n        sage: QQ(mpq('3/4'))\n        3/4\n        sage: QQ(mpz(42))\n        42\n        sage: Rational(mpq(2/3))\n        2/3\n        sage: Rational(mpz(5))\n        5\n\n    TESTS:\n\n    Check that :issue:`28321` is fixed::\n\n        sage: QQ((2r^100r, 3r^100r))\n        1267650600228229401496703205376/515377520732011331036461129765621272702107522001\n        sage: QQ((-2r^100r, -3r^100r))\n        1267650600228229401496703205376/515377520732011331036461129765621272702107522001\n    \")},\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "a = -2/3\n        sage: type(a)\n        <class 'sage.rings.rational.Rational'>\n        sage: parent(a)\n        Rational Field\n        sage: Rational('1/0')\n        Traceback (most recent call last):\n        ...\n        TypeError: unable to convert '1/0' to a rational\n        sage: Rational(1.5)\n        3/2\n        sage: Rational('9/6')\n        3/2\n        sage: Rational((2^99,2^100))\n        1/2\n        sage: Rational((\\"2\\", \\"10\\"), 16)\n        1/8\n        sage: Rational(QQbar(125/8).nth_root(3))                                        # needs sage.rings.number_field\n        5/2\n        sage: Rational(AA(209735/343 - 17910/49*golden_ratio).nth_root(3)               # needs sage.rings.number_field sage.symbolic\n\n",
    "          + 3*AA(golden_ratio))\n        53/7\n        sage: QQ(float(1.5))\n        3/2\n        sage: QQ(RDF(1.2))\n        6/5\n\n    Conversion from fractions::\n\n        sage: import fractions\n        sage: f = fractions.Fraction(1r, 2r)\n        sage: Rational(f)\n        1/2\n\n    Conversion from PARI::\n\n        sage: Rational(pari('-939082/3992923'))                                         # needs sage.libs.pari\n        -939082/3992923\n        sage: Rational(pari('Pol([-1/2])'))  #9595                                      # needs sage.libs.pari\n        -1/2\n\n    Conversions from numpy::\n\n        sage: # needs numpy\n        sage: import numpy as np\n        sage: QQ(np.int8('-15'))\n        -15\n        sage: QQ(np.int16('-32'))\n        -32\n        sage: QQ(np.int32('-19'))\n        -19\n        sage: QQ(np.uint32('1412'))\n        1412\n\n        sage: QQ(np.float16('12'))                                                      # needs numpy\n        12\n\n    Conversions from gmpy2::\n\n      \"\"  sage: from gmpy2 import *\n        sage: QQ(mpq('3/4'))\n        3/4\n        sage: QQ(mpz(42))\n        42\n        sage: Rational(mpq(2/3))\n        2/3\n        sage: Rational(mpz(5))\n        5\n\n    TESTS:\n\n    Check that :issue:`28321` is fixed::\n\n        sage: QQ((2r^100r, 3r^100r))\n        1267650600228229401496703205376/515377520732011331036461129765621272702107522001\n        sage: QQ((-2r^100r, -3r^100r))\n        1267650600228229401496703205376/515377520732011331036461129765621272702107522001\n    \"), /*tp_doc*/\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    " "
   ]
  }
],
"metadata": {
 "kernelspec": {
  "display_name": "SageMath 10.6",
  "language": "sage",
  "name": "sagemath"
 },
 "language_info": {
  "codemirror_mode": {
   "name": "ipython",
   "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
