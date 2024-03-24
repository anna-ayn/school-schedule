from sage.sat.solvers.dimacs import DIMACS

solver = DIMACS()
solver.add_clause([1, 2, 3])
solver.add_clause([-1, -2, -3])

print(solver.nvars())

