{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import cvxpy\n        sage: cvxpy.installed_solvers()                                                # random\n\n    Using the default solver determined by CVXPY::\n\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY'); p.solve()\n        0.0\n\n    Using a specific solver::\n\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/OSQP'); p.solve()\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/ECOS'); p.solve()\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/SCS'); p.solve()\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/SciPy/HiGHS'); p.solve()\n        0.0\n\n    Open-source solvers provided by optional packages::\n\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/GLPK'); p.solve()             # needs cvxopt\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/GLPK_MI'); p.solve()          # needs cvxopt\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/CVXOPT'); p.solve()           # needs cvxopt\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/GLOP'); p.solve()            # optional - ortools\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/PDLP'); p.solve()            # optional - ortools\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/CBC'); p.solve()             # optional - cylp\n        0.0\n\n    Non-free solvers::\n\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/Gurobi'); p.solve()          # optional - gurobi\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/CPLEX'); p.solve()           # optio\"\"nal - cplex\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/MOSEK'); p.solve()           # optional - mosek\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/SCIP'); p.solve()            # optional - pyscipopt\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/XPRESS'); p.solve()          # optional - xpress\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver=\\"CVXPY/NAG\\"); p.solve()             # optional - naginterfaces\n        0.0\n    \")},"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import cvxpy\n        sage: cvxpy.installed_solvers()                                                # random\n\n    Using the default solver determined by CVXPY::\n\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY'); p.solve()\n        0.0\n\n    Using a specific solver::\n\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/OSQP'); p.solve()\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/ECOS'); p.solve()\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/SCS'); p.solve()\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/SciPy/HiGHS'); p.solve()\n        0.0\n\n    Open-source solvers provided by optional packages::\n\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/GLPK'); p.solve()             # needs cvxopt\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/GLPK_MI'); p.solve()          # needs cvxopt\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/CVXOPT'); p.solve()           # needs cvxopt\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/GLOP'); p.solve()            # optional - ortools\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/PDLP'); p.solve()            # optional - ortools\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/CBC'); p.solve()             # optional - cylp\n        0.0\n\n    Non-free solvers::\n\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/Gurobi'); p.solve()          # optional - gurobi\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/CPLEX'); p.solve()           # optio\"\"nal - cplex\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/MOSEK'); p.solve()           # optional - mosek\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/SCIP'); p.solve()            # optional - pyscipopt\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver='CVXPY/XPRESS'); p.solve()          # optional - xpress\n        0.0\n        sage: p = MixedIntegerLinearProgram(solver=\\"CVXPY/NAG\\"); p.solve()             # optional - naginterfaces\n        0.0\n    \"), /*tp_doc*/"
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
