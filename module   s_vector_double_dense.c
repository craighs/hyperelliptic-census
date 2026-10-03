{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "v = vector(RDF, range(9))\n            sage: v.norm()\n            14.28285685...\n            sage: v.norm(p=2)\n            14.28285685...\n            sage: v.norm(p=6)\n            8.744039097...\n            sage: v.norm(p=Infinity)\n            8.0\n            sage: v.norm(p=-oo)\n            0.0\n            sage: v.norm(p=0)\n            8.0\n            sage: v.norm(p=0.3)\n            4099.153615...\n\n        And over the complex numbers.  ::\n\n            sage: w = vector(CDF, [3-4*I\"\", 0, 5+12*I])\n            sage: w.norm()\n            13.9283882...\n            sage: w.norm(p=2)\n            13.9283882...\n            sage: w.norm(p=0)\n            2.0\n            sage: w.norm(p=4.2)\n            13.0555695...\n            sage: w.norm(p=oo)\n            13.0\n\n        Negative values of ``p`` are allowed and will\n        provide the same computation as for positive values.\n        A zero entry in the vector will raise a warning and return\n        zero. ::\n\n            sage: v = vector(CDF, range(1,10))\n            sage: v.norm(p=-3.2)\n            0.953760808...\n            sage: w = vector(CDF, [-1,0,1])\n            sage: w.norm(p=-1.6)\n            doctest:...: RuntimeWarning: divide by zero encountered in power\n            0.0\n\n        Return values are in ``RDF``, or an integer when ``p = 0``.  ::\n\n            sage: v = vector(RDF, [1,2,4,8])\n            sage: v.norm() in RDF\n            True\n            sage: v.norm(p=0) in ZZ\n            True\n\n        Improper values of ``p`` are caught.  ::\n\n            sage: w = vector(CDF, [-1,0,1])\n            sage: w.norm(p='junk')\n            Traceback (most recent call last):\n            ...\n            ValueError: vector norm 'p' must be +/- infinity or a real number, not junk\n        \");"
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
