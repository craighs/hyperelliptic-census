{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "A = matrix(RDF, 3, range(-3, 6)); A\n            [-3.0 -2.0 -1.0]\n            [ 0.0  1.0  2.0]\n            [ 3.0  4.0  5.0]\n            sage: A.norm()\n            7.99575670...\n            sage: A.norm(p='frob')\n            8.30662386...\n            sage: A.norm(p=Infinity)\n            12.0\n            sage: A.norm(p=-Infinity)\n            3.0\n            sage: A.norm(p=1)\"\"\n            8.0\n            sage: A.norm(p=-1)\n            6.0\n            sage: A.norm(p=2)\n            7.99575670...\n            sage: A.norm(p=-2) < 10^-15\n            True\n\n        And over the complex numbers.  ::\n\n            sage: # needs sage.symbolic\n            sage: B = matrix(CDF, 2, [[1+I, 2+3*I],[3+4*I,3*I]]); B\n            [1.0 + 1.0*I 2.0 + 3.0*I]\n            [3.0 + 4.0*I       3.0*I]\n            sage: B.norm()\n            6.66189877...\n            sage: B.norm(p='frob')\n            7.0\n            sage: B.norm(p=Infinity)\n            8.0\n            sage: B.norm(p=-Infinity)\n            5.01976483...\n            sage: B.norm(p=1)\n            6.60555127...\n            sage: B.norm(p=-1)\n            6.41421356...\n            sage: B.norm(p=2)\n            6.66189877...\n            sage: B.norm(p=-2)\n            2.14921023...\n\n        Since it is invariant under unitary multiplication, the\n        Frobenius norm is equal to the square root of the sum of\n        squares of the singular values.  ::\n\n            sage: A = matrix(RDF, 5, range(1,26))\n            sage: f = A.norm(p='frob')\n            sage: U, S, V = A.SVD()\n            sage: s = sqrt(sum([S[i,i]^2 for i in range(5)]))\n            sage: abs(f-s) < 1.0e-12\n            True\n\n        Return values are in `RDF`. ::\n\n            sage: A = matrix(CDF, 2, range(4))\n            sage: A.norm() in RDF\n            True\n\n        Improper values of ``p`` are caught.  ::\n\n            sage: A.norm(p='bogus')\n            Traceback (most recent call last):\n            ...\n            ValueError: matrix norm 'p' must be +/- infinity, 'frob' or an integer, not bogus\n            sage: A.norm(p=632)\n            Traceback (most recent call last):\n            ...\n            ValueError: matrix norm integer values of 'p' must be -2, -1, 1 or 2, not 632\n        \");"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "A = matrix(QQ, [[ 1,  0,  0,  0,  0,  1,  3],\n\n",
    "                 [-2,  1,  1, -2,  0, -4,  0],\n\n",
    "                 [ 1,  0,  1, -4, -6, -3,  7],\n\n",
    "                 [-2,  2,  1,  1,  7,  1, -1],\n\n",
    "                 [-1,  0, -1,  5,  8,  4, -6],\n\n",
    "                 [ 4, -2, -2,  1, -3,  0,  8],\n\n",
    "                 [-2,  1,  0,  2,  7,  3, -4]])\n            sage: A.determinant()\n            1\n            sage: B = A.change_ring(RDF)\n            sage: sv = B.singular_values(); sv  # tol 1e-12\n            [20.523980658874265, 8.486837028536643, 5.86168134845073, 2.4429165899286978, 0.5831970144724045, 0.26933287286576313, 0.0025524488076110402]\n            sage: prod(sv)  # tol 1e-12\n            0.9999999999999525\n\n        An exact matrix that is obviously not of full rank, and then\n        a computation of the singular values after conversion\n        to an approximate matrix. ::\n\n            sage: A = matrix(QQ, [[1/3, 2/3, 11/3],\n\n",
    "                 [2/3, 1/3,  7/3],\n\n",
    "                 [2/3, 5/3, 27/3]])\n            sage: A.rank()\n            2\n            sage: B \"\"= A.change_ring(CDF)\n            sage: sv = B.singular_values()\n            sage: sv[0:2]\n            [10.1973039..., 0.487045871...]\n            sage: sv[2] < 1e-14\n            True\n\n        A matrix of rank 3 over the complex numbers.  ::\n\n            sage: A = matrix(CDF, [[46*I - 28, -47*I - 50, 21*I + 51, -62*I - 782, 13*I + 22],\n\n",
    "                  [35*I - 20, -32*I - 46, 18*I + 43, -57*I - 670, 7*I + 3],\n\n",
    "                  [22*I - 13, -23*I - 23, 9*I + 24, -26*I - 347, 7*I + 13],\n\n",
    "                  [-44*I + 23, 41*I + 57, -19*I - 54, 60*I + 757, -11*I - 9],\n\n",
    "                  [30*I - 18, -30*I - 34, 14*I + 34, -42*I - 522, 8*I + 12]])\n            sage: sv = A.singular_values()\n            sage: sv[0:3]  # tol 1e-14\n            [1440.7336659952966, 18.404403413369227, 6.839707797136151]\n            sage: (sv[3] < 10^-13) or sv[3]\n            True\n            sage: (sv[4] < 10^-14) or sv[4]\n            True\n\n        A full-rank matrix that is ill-conditioned.  We use this to\n        illustrate ways of using the various possibilities for ``eps``,\n        including one that is ill-advised. Notice that the automatically\n        computed cutoff gets this (difficult) example slightly wrong.\n        This illustrates the impossibility of any automated process always\n        getting this right.  Use with caution and judgement.  ::\n\n            sage: entries = [1/(i+j+1) for i in range(12) for j in range(12)]\n            sage: B = matrix(QQ, 12, 12, entries)\n            sage: B.rank()\n            12\n            sage: A = B.change_ring(RDF)\n            sage: A.condition() > 1.59e16 or A.condition()\n            True\n\n            sage: A.singular_values(eps=None)  # abs tol 7e-16\n            [1.7953720595619975, 0.38027524595503703, 0.04473854875218107, 0.0037223122378911614, 0.0002330890890217751, 1.116335748323284e-05, 4.082376110397296e-07, 1.1228610675717613e-08, 2.2519\"\"645713496478e-10, 3.1113486853814003e-12, 2.6500422260778388e-14, 9.87312834948426e-17]\n            sage: A.singular_values(eps='auto')  # abs tol 7e-16\n            [1.7953720595619975, 0.38027524595503703, 0.04473854875218107, 0.0037223122378911614, 0.0002330890890217751, 1.116335748323284e-05, 4.082376110397296e-07, 1.1228610675717613e-08, 2.2519645713496478e-10, 3.1113486853814003e-12, 2.6500422260778388e-14, 0.0]\n            sage: A.singular_values(eps=1e-4)  # abs tol 7e-16\n            [1.7953720595619975, 0.38027524595503703, 0.04473854875218107, 0.0037223122378911614, 0.0002330890890217751, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]\n\n        With Sage's \\"verbose\\" facility, you can compactly see the cutoff\n        at work.  In any application of this routine, or those that build upon\n        it, it would be a good idea to conduct this exercise on samples.\n        We also test here that all the  values are returned in `RDF` since\n        singular values are always real. ::\n\n            sage: A = matrix(CDF, 4, range(16))\n            sage: from sage.misc.verbose import set_verbose\n            sage: set_verbose(1)\n            sage: sv = A.singular_values(eps='auto'); sv\n            verbose 1 (<module>) singular values,\n            smallest-non-zero:cutoff:largest-zero,\n            2.2766...:6.2421...e-14:...\n            [35.13996365902..., 2.27661020871472..., 0.0, 0.0]\n            sage: set_verbose(0)\n\n            sage: all(s in RDF for s in sv)\n            True\n\n        TESTS:\n\n        Bogus values of the ``eps`` keyword will be caught::\n\n            sage: A.singular_values(eps='junk')\n            Traceback (most recent call last):\n            ...\n            ValueError: could not convert string to float: ...\n\n        AUTHOR:\n\n        - Rob Beezer - (2011-02-18)\n        \");\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "m = matrix(RDF, 2, 2, [1,2,3,4])\n            sage: ev = m.eigenvalues(); ev\n            [-0.372281323..., 5.37228132...]\n            sage: ev[0].parent()\n            Comp\"\"lex Double Field\n\n            sage: m = matrix(RDF, 2, 2, [0,1,-1,0])\n            sage: m.eigenvalues(algorithm='default')\n            [1.0*I, -1.0*I]\n\n            sage: m = matrix(CDF, 2, 2, [I,1,-I,0])                                     # needs sage.symbolic\n            sage: m.eigenvalues()                                                       # needs sage.symbolic\n            [-0.624810533... + 1.30024259...*I, 0.624810533... - 0.30024259...*I]\n\n        The adjacency matrix of a graph will be symmetric, and the\n        eigenvalues will be real.  ::\n\n            sage: # needs sage.graphs\n            sage: A = graphs.PetersenGraph().adjacency_matrix()\n            sage: A = A.change_ring(RDF)\n            sage: ev = A.eigenvalues(algorithm='symmetric'); ev  # tol 1e-14\n            [-2.0, -2.0, -2.0, -2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 3.0]\n            sage: ev[0].parent()\n            Real Double Field\n\n        The matrix ``A`` is \\"random\\", but the construction of ``C``\n        provides a positive-definite Hermitian matrix.  Note that\n        the eigenvalues of a Hermitian matrix are real, and the\n        eigenvalues of a positive-definite matrix will be positive.  ::\n\n            sage: # needs sage.symbolic\n            sage: A = matrix([[ 4*I + 5,  8*I + 1,  7*I + 5, 3*I + 5],\n\n",
    "             [ 7*I - 2, -4*I + 7, -2*I + 4, 8*I + 8],\n\n",
    "             [-2*I + 1,  6*I + 6,  5*I + 5,  -I - 4],\n\n",
    "             [ 5*I + 1,  6*I + 2,    I - 4, -I + 3]])\n            sage: C = (A*A.conjugate_transpose()).change_ring(CDF)\n            sage: ev = C.eigenvalues(algorithm='hermitian'); ev\n            [2.68144025..., 49.5167998..., 274.086188..., 390.71557...]\n            sage: ev[0].parent()\n            Real Double Field\n\n        A tolerance can be given to aid in grouping eigenvalues that\n        are similar numerically.  However, if the parameter is too small\n        it might split too finely.  Too lar\"\"ge, and it can go wrong very\n        badly.  Use with care.  ::\n\n            sage: # needs sage.graphs\n            sage: G = graphs.PetersenGraph()\n            sage: G.spectrum()\n            [3, 1, 1, 1, 1, 1, -2, -2, -2, -2]\n            sage: A = G.adjacency_matrix().change_ring(RDF)\n            sage: A.eigenvalues(algorithm='symmetric', tol=1.0e-5)  # tol 1e-15\n            [(-2.0, 4), (1.0, 5), (3.0, 1)]\n            sage: A.eigenvalues(algorithm='symmetric', tol=2.5)  # tol 1e-15\n            [(-2.0, 4), (1.3333333333333333, 6)]\n\n        An (extreme) example of properly grouping similar eigenvalues.  ::\n\n            sage: # needs sage.graphs\n            sage: G = graphs.HigmanSimsGraph()\n            sage: A = G.adjacency_matrix().change_ring(RDF)\n            sage: A.eigenvalues(algorithm='symmetric', tol=1.0e-5)  # tol 2e-15\n            [(-8.0, 22), (2.0, 77), (22.0, 1)]\n\n        In this generalized eigenvalue problem, the homogeneous coordinates\n        explain the output obtained for the eigenvalues::\n\n            sage: A = matrix.identity(RDF, 2)\n            sage: B = matrix(RDF, [[3, 5], [6, 10]])\n            sage: A.eigenvalues(B)  # tol 1e-14\n            [0.0769230769230769, +infinity]\n            sage: E = A.eigenvalues(B, homogeneous=True); E  # random\n            [(0.9999999999999999, 13.000000000000002), (0.9999999999999999, 0.0)]\n            sage: [alpha/beta for alpha, beta in E]  # tol 1e-14\n            [0.0769230769230769, NaN + NaN*I]\n\n        .. SEEALSO::\n\n            :meth:`eigenvectors_left`,\n            :meth:`eigenvectors_right`,\n            :meth:`.Matrix.eigenmatrix_left`,\n            :meth:`.Matrix.eigenmatrix_right`.\n\n        TESTS:\n\n        Testing bad input.  ::\n\n            sage: A = matrix(CDF, 2, range(4))\n            sage: A.eigenvalues(algorithm='junk')\n            Traceback (most recent call last):\n            ...\n            ValueError: algorithm must be 'default', 'symmetric', or 'her\"\"mitian', not junk\n\n            sage: A = matrix(CDF, 2, 3, range(6))\n            sage: A.eigenvalues()\n            Traceback (most recent call last):\n            ...\n            ValueError: matrix must be square, not 2 x 3\n            sage: matrix.identity(CDF, 2).eigenvalues(A)\n            Traceback (most recent call last):\n            ...\n            ValueError: other matrix must be square, not 2 x 3\n\n            sage: A = matrix(CDF, 2, [1, 2, 3, 4*I])\n            sage: A.eigenvalues(algorithm='symmetric')\n            Traceback (most recent call last):\n            ...\n            TypeError: cannot apply symmetric algorithm to matrix with complex entries\n\n            sage: A = matrix(CDF, 2, 2, range(4))\n            sage: A.eigenvalues(tol='junk')\n            Traceback (most recent call last):\n            ...\n            TypeError: tolerance parameter must be a real number, not junk\n\n            sage: A = matrix(CDF, 2, 2, range(4))\n            sage: A.eigenvalues(tol=-0.01)\n            Traceback (most recent call last):\n            ...\n            ValueError: tolerance parameter must be positive, not -0.01\n\n        A very small matrix.  ::\n\n            sage: matrix(CDF,0,0).eigenvalues()\n            []\n\n        Check that homogeneous coordinates work for hermitian positive definite\n        input::\n\n            sage: A = matrix.identity(CDF, 2)\n            sage: B = matrix(CDF, [[2, 1+I], [1-I, 3]])\n            sage: A.eigenvalues(B, algorithm='hermitian', homogeneous=True)  # tol 1e-14\n            [(0.25, 1.0), (1.0, 1.0)]\n\n        Test the deprecation::\n\n            sage: # needs sage.graphs\n            sage: A = graphs.PetersenGraph().adjacency_matrix().change_ring(RDF)\n            sage: ev = A.eigenvalues('symmetric', 1e-13)\n            doctest:...: DeprecationWarning: \\"algorithm\\" and \\"tol\\" should be used\n            as keyword argument only\n            See https://github.com/sagemath/sage/issues/29243 for \"\"details.\n            sage: ev  # tol 1e-13\n            [(-2.0, 4), (1.0, 5), (3.0, 1)]\n            sage: A.eigenvalues('symmetric', 1e-13, tol=1e-12)\n            Traceback (most recent call last):\n            ...\n            TypeError: eigenvalues() got multiple values for keyword argument 'tol'\n            sage: A.eigenvalues('symmetric', algorithm='hermitian')\n            Traceback (most recent call last):\n            ...\n            TypeError: eigenvalues() got multiple values for keyword argument 'algorithm'\n        \");\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "m = matrix(RDF, [[-5, 3, 2, 8],[10, 2, 4, -2],[-1, -10, -10, -17],[-2, 7, 6, 13]])\n            sage: m\n            [ -5.0   3.0   2.0   8.0]\n            [ 10.0   2.0   4.0  -2.0]\n            [ -1.0 -10.0 -10.0 -17.0]\n            [ -2.0   7.0   6.0  13.0]\n            sage: spectrum = m.left_eigenvectors()\n            sage: for i in range(len(spectrum)):\n\n",
    "     spectrum[i][1][0] = matrix(RDF, spectrum[i][1]).echelon_form()[0]\n            sage: spectrum[0]  # tol 1e-13\n            (2.0, [(1.0, 1.0, 1.0, 1.0)], 1)\n            sage: spectrum[1]  # tol 1e-13\n            (1.0, [(1.0, 0.8, 0.8, 0.6)], 1)\n            sage: spectrum[2]  # tol 1e-13\n            (-2.0, [(1.0, 0.4, 0.6, 0.2)], 1)\n            sage: spectrum[3]  # tol 1e-13\n            (-1.0, [(1.0, 1.0, 2.0, 2.0)], 1)\n\n        A generalized eigenvalue problem::\n\n            sage: A = matrix(CDF, [[1+I, -2], [3, 4]])\n            sage: B = matrix(CDF, [[0, 7-I], [2, -3]])\n            sage: E = A.eigenvectors_left(B)\n            sage: all((v * A - e * v * B).norm() < 1e-14 for e, [v], _ in E)\n            True\n\n        In a generalized eigenvalue problem with a singular matrix `B`, we can\n        check the eigenvector property using homogeneous coordinates, even\n        though the quotient `\\alpha/\\beta` is not always defined::\n\n            sage: A = matrix.identity(CDF, 2)\n            sage: B = matrix(CDF, [[2, 1+I], [4, 2+2*I]])\n            sage: E = A.eigenvectors_left(B, homogeneous=True)\n            sage: all((beta * v * A - alpha * v * B).norm() < 1e-14\n\n",
    "     for (alpha, beta), [v], _ in E)\n        \"\"    True\n\n        .. SEEALSO::\n\n            :meth:`eigenvalues`,\n            :meth:`eigenvectors_right`,\n            :meth:`.Matrix.eigenmatrix_left`.\n\n        TESTS:\n\n        The following example shows that :issue:`20439` has been resolved::\n\n            sage: A = matrix(CDF, [[-2.53634347567,  2.04801738686, -0.0, -62.166145304],\n\n",
    "                  [ 0.7, -0.6, 0.0, 0.0],\n\n",
    "                  [0.547271128842, 0.0, -0.3015, -21.7532081652],\n\n",
    "                  [0.0, 0.0, 0.3, -0.4]])\n            sage: spectrum = A.left_eigenvectors()\n            sage: all((Matrix(spectrum[i][1])*(A - spectrum[i][0])).norm() < 10^(-2)\n\n",
    "     for i in range(A.nrows()))\n            True\n\n        The following example shows that the fix for :issue:`20439` (conjugating\n        eigenvectors rather than eigenvalues) is the correct one::\n\n            sage: A = Matrix(CDF,[[I,0],[0,1]])\n            sage: spectrum = A.left_eigenvectors()\n            sage: for i in range(len(spectrum)):\n\n",
    "   spectrum[i][1][0] = matrix(CDF, spectrum[i][1]).echelon_form()[0]\n            sage: spectrum\n            [(1.0*I, [(1.0, 0.0)], 1), (1.0, [(0.0, 1.0)], 1)]\n        \");\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "m = matrix(RDF, [[-9, -14, 19, -74],[-1, 2, 4, -11],[-4, -12, 6, -32],[0, -2, -1, 1]])\n            sage: m\n            [ -9.0 -14.0  19.0 -74.0]\n            [ -1.0   2.0   4.0 -11.0]\n            [ -4.0 -12.0   6.0 -32.0]\n            [  0.0  -2.0  -1.0   1.0]\n            sage: spectrum = m.right_eigenvectors()\n            sage: for i in range(len(spectrum)):\n\n",
    "   spectrum[i][1][0] = matrix(RDF, spectrum[i][1]).echelon_form()[0]\n            sage: spectrum[0]  # tol 1e-13\n            (2.0, [(1.0, -2.0, 3.0, 1.0)], 1)\n            sage: spectrum[1]  # tol 1e-13\n            (1.0, [(1.0, -0.666666666666633, 1.333333333333286, 0.33333333333331555)], 1)\n            sage: spectrum[2]  # tol 1e-13\n            (-2.0, [(1.0, -0.2, 1.0, 0.2)], 1)\n            sage: spectrum[3]  # tol 1e-12\n            (-1.0, [(1.0, -0.5, 2.0, 0.5)], 1)\n\n        A generalized eigenvalue problem::\n\n            sage: A = matrix(CDF, [[1+I, -2], [3, 4]])\n            sage: B = matrix(CDF, [[0, 7-I], [2, -3]])\n            sage: E = A.eigenvectors_right(B)\n            sage: all((A * v - e * B * v).norm() < 1e-14 for e, [v], _ in E)\n            True\n\n        In a generalized eigenvalue problem with a singular matrix `B`, we can\n        check the eigenvector property using homogeneous coordinates, even\n        though the quotient `\\alpha/\\beta` is not always defined::\n\n            sage: A = matrix.identity(RDF, 2)\n            sage: B = matrix(RDF, [[3, 5], [6, 10]])\n            sage: E = A.eigenvectors_right(B, homogeneous=True)\n            sage: all((beta * A * v - alpha * B * v).norm() < 1e-14\n            \"\"\n",
    "     for (alpha, beta), [v], _ in E)\n            True\n\n        .. SEEALSO::\n\n            :meth:`eigenvalues`,\n            :meth:`eigenvectors_left`,\n            :meth:`.Matrix.eigenmatrix_right`.\n\n        TESTS:\n\n        The following example shows that :issue:`20439` has been resolved::\n\n            sage: A = matrix(CDF, [[-2.53634347567,  2.04801738686, -0.0, -62.166145304],\n\n",
    "                  [ 0.7, -0.6, 0.0, 0.0],\n\n",
    "                  [0.547271128842, 0.0, -0.3015, -21.7532081652],\n\n",
    "                  [0.0, 0.0, 0.3, -0.4]])\n            sage: spectrum = A.right_eigenvectors()\n            sage: all(((A - spectrum[i][0]) * Matrix(spectrum[i][1]).transpose()).norm() < 10^(-2)\n\n",
    "     for i in range(A.nrows()))\n            True\n\n        The following example shows that the fix for :issue:`20439` (conjugating\n        eigenvectors rather than eigenvalues) is the correct one::\n\n            sage: A = Matrix(CDF,[[I,0],[0,1]])\n            sage: spectrum = A.right_eigenvectors()\n            sage: for i in range(len(spectrum)):\n\n",
    "     spectrum[i][1][0] = matrix(CDF, spectrum[i][1]).echelon_form()[0]\n            sage: spectrum\n            [(1.0*I, [(1.0, 0.0)], 1), (1.0, [(0.0, 1.0)], 1)]\n        \");\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# needs sage.symbolic\n            sage: A = matrix(CDF, [[1, 2], [3, 3+I]])\n            sage: b = matrix(CDF, [[1, 0], [2, 1]])\n            sage: x = A._solve_right_nonsingular_square(b)\n            sage: (A * x - b).norm() < 1e-14\n            True\n        \");"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "A = matrix(RDF, 3, 2, [1, 3, 4, 2, 0, -3])\n            sage: b = matrix(RDF, 3, 2, [5, 6, 1, 0, 0, 2])\n            sage: x = A._solve_right_general(b)\n            sage: y = ~(A.T * A) * A.T * b  # closed form solution\n            sage: (x - y).norm() < 1e-14\n            True\n        \");"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "m = matrix(RDF,2,range(4)); m.det()\n            -2.0\n            sage: m = matrix(RDF,0,[]); m.det()\n            1.0\n            sage: m = matrix(RDF, 2, range(6)); m.det()\n            Traceback (most recent call last):\n            ...\n            ValueError: self must be a square matrix\n        \");"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "A = matrix(RDF, [[-2, 0, -4, -1, -1],\n\n",
    "                  [-2, 1, -6, -3, -1],\n\n",
    "                  [1, 1, 7, 4, 5],\n\n",
    "                  [3, 0, 8, 3, 3],\n\n",
    "                  [-1, 1, -6, -6, 5]])\n            sage: Q, R = A.QR()\n\n        At this point, ``Q`` is only well-defined up to the\n        signs of its columns, and similarly for ``R`` and its\n        rows, so we normalize them::\n\n            sage: Qnorm = Q._normalize_columns()\n            sage: Rnorm = R._normalize_rows()\"\"\n            sage: Qnorm.round(6).zero_at(10^-6)\n            [ 0.458831  0.126051  0.381212  0.394574   0.68744]\n            [ 0.458831  -0.47269 -0.051983 -0.717294  0.220963]\n            [-0.229416 -0.661766  0.661923  0.180872 -0.196411]\n            [-0.688247 -0.189076 -0.204468  -0.09663  0.662889]\n            [ 0.229416 -0.535715 -0.609939  0.536422 -0.024551]\n            sage: Rnorm.round(6).zero_at(10^-6)\n            [ 4.358899 -0.458831 13.076697  6.194225  2.982405]\n            [      0.0  1.670172  0.598741  -1.29202  6.207997]\n            [      0.0       0.0  5.444402  5.468661 -0.682716]\n            [      0.0       0.0       0.0  1.027626   -3.6193]\n            [      0.0       0.0       0.0       0.0  0.024551]\n            sage: (Q*Q.transpose())  # tol 1e-14\n            [0.9999999999999994                0.0                0.0                0.0                0.0]\n            [               0.0                1.0                0.0                0.0                0.0]\n            [               0.0                0.0 0.9999999999999999                0.0                0.0]\n            [               0.0                0.0                0.0 0.9999999999999998                0.0]\n            [               0.0                0.0                0.0                0.0 1.0000000000000002]\n            sage: (Q*R - A).zero_at(10^-14)\n            [0.0 0.0 0.0 0.0 0.0]\n            [0.0 0.0 0.0 0.0 0.0]\n            [0.0 0.0 0.0 0.0 0.0]\n            [0.0 0.0 0.0 0.0 0.0]\n            [0.0 0.0 0.0 0.0 0.0]\n\n        Now over the complex numbers, demonstrating that the SciPy libraries\n        are (properly) using the Hermitian inner product, so that ``Q`` is\n        a unitary matrix (its inverse is the conjugate-transpose).  ::\n\n            sage: A = matrix(CDF, [[-8, 4*I + 1, -I + 2, 2*I + 1],\n\n",
    "                  [1, -2*I - 1, -I + 3, -I + 1],\n\n",
    "                  [I + 7, 2*I + 1, -2*I + 7, -I \"\"+ 1],\n\n",
    "                  [I + 2, 0, I + 12, -1]])\n            sage: Q, R = A.QR()\n            sage: Q._normalize_columns()  # tol 1e-6\n            [                           0.7302967433402214    0.20705664550556482 + 0.5383472783144685*I   0.24630498099986423 - 0.07644563587232917*I   0.23816176831943323 - 0.10365960327796941*I]\n            [                         -0.09128709291752768  -0.20705664550556482 - 0.37787837804765584*I   0.37865595338630315 - 0.19522214955246678*I    0.7012444502144682 - 0.36437116509865947*I]\n            [  -0.6390096504226938 - 0.09128709291752768*I    0.17082173254209104 + 0.6677576817554466*I -0.03411475806452064 + 0.040901987417671426*I   0.31401710855067644 - 0.08251917187054114*I]\n            [ -0.18257418583505536 - 0.09128709291752768*I  -0.03623491296347384 + 0.07246982592694771*I    0.8632284069415112 + 0.06322839976356195*I  -0.44996948676115206 - 0.01161191812089182*I]\n            sage: R._normalize_rows().zero_at(1e-15)  # tol 1e-6\n            [                        10.954451150103322                      -1.9170289512680814*I   5.385938482134133 - 2.1908902300206643*I -0.2738612787525829 - 2.1908902300206643*I]\n            [                                       0.0                            4.8295962564173  -0.8696379111233719 - 5.864879483945123*I  0.993871898426711 - 0.30540855212070794*I]\n            [                                       0.0                                        0.0                          12.00160760935814 -0.2709533402297273 + 0.4420629644486325*I]\n            [                                       0.0                                        0.0                                        0.0                         1.9429639442589917]\n            sage: (Q.conjugate().transpose()*Q).zero_at(1e-15)  # tol 1e-15\n            [               1.0                0.0                0.0                0.0]\n            [               0.0 0.9999999999999994                0\"\".0                0.0]\n            [               0.0                0.0 1.0000000000000002                0.0]\n            [               0.0                0.0                0.0 1.0000000000000004]\n            sage: (Q*R - A).zero_at(10^-14)\n            [0.0 0.0 0.0 0.0]\n            [0.0 0.0 0.0 0.0]\n            [0.0 0.0 0.0 0.0]\n            [0.0 0.0 0.0 0.0]\n\n        An example of a rectangular matrix that is also rank-deficient.\n        If you run this example yourself, you may see a very small, nonzero\n        entries in the third row, in the third column, even though the exact\n        version of the matrix has rank 2.  The final two columns of ``Q``\n        span the left kernel of ``A`` (as evidenced by the two zero rows of\n        ``R``).  Different platforms will compute different bases for this\n        left kernel, so we do not exhibit the actual matrix.  ::\n\n            sage: Arat = matrix(QQ, [[2, -3, 3],\n\n",
    "                    [-1, 1, -1],\n\n",
    "                    [-1, 3, -3],\n\n",
    "                    [-5, 1, -1]])\n            sage: Arat.rank()\n            2\n            sage: A = Arat.change_ring(CDF)\n            sage: Q, R = A.QR()\n            sage: R._normalize_rows()  # abs tol 1e-14\n            [     5.567764362830022    -2.6940795304016243     2.6940795304016243]\n            [                   0.0     3.5695847775155825    -3.5695847775155825]\n            [                   0.0                    0.0 2.4444034681064287e-16]\n            [                   0.0                    0.0                    0.0]\n            sage: (Q.conjugate_transpose()*Q)  # abs tol 1e-14\n            [     1.0000000000000002  -5.185196889911925e-17 -4.1457180570414476e-17  -2.909388767229071e-17]\n            [ -5.185196889911925e-17      1.0000000000000002  -9.286869233696149e-17 -1.1035822863186828e-16]\n            [-4.1457180570414476e-17  -9.286869233696149e-17                     1.0  4.41592\"\"15672155694e-17]\n            [ -2.909388767229071e-17 -1.1035822863186828e-16  4.4159215672155694e-17                     1.0]\n\n        Results are cached, meaning they are immutable matrices.\n        Make a copy if you need to manipulate a result. ::\n\n            sage: A = random_matrix(CDF, 2, 2)\n            sage: Q, R = A.QR()\n            sage: Q.is_mutable()\n            False\n            sage: R.is_mutable()\n            False\n            sage: Q[0,0] = 0\n            Traceback (most recent call last):\n            ...\n            ValueError: matrix is immutable; please change a copy instead (i.e., use copy(M) to change a copy of M).\n            sage: Qcopy = copy(Q)\n            sage: Qcopy[0,0] = 679\n            sage: Qcopy[0,0]\n            679.0\n\n        TESTS:\n\n        Trivial cases return trivial results of the correct size,\n        and we check ``Q`` itself in one case, verifying a fix for\n        :issue:`10795`.  ::\n\n            sage: A = zero_matrix(RDF, 0, 10)\n            sage: Q, R = A.QR()\n            sage: Q.nrows(), Q.ncols()\n            (0, 0)\n            sage: R.nrows(), R.ncols()\n            (0, 10)\n            sage: A = zero_matrix(RDF, 3, 0)\n            sage: Q, R = A.QR()\n            sage: Q.nrows(), Q.ncols()\n            (3, 3)\n            sage: R.nrows(), R.ncols()\n            (3, 0)\n            sage: Q\n            [1.0 0.0 0.0]\n            [0.0 1.0 0.0]\n            [0.0 0.0 1.0]\n        \");\n"
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
