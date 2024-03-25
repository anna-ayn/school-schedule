from sage.sat.solvers.dimacs import DIMACS
# from prettytable import PrettyTable
from prettytable.colortable import ColorTable, Themes

solver = DIMACS()
solver.add_clause([1, 2, 3])
solver.add_clause([-1, -2, -3])

print(solver.nvars())

table = ColorTable(theme=Themes.OCEAN)
table.field_names = ["City name", "Area", "Population", "Annual Rainfall"]
table.add_rows(
    [
        ["Adelaide", 1295, 1158259, 600.5],
        ["Brisbane", 5905, 1857594, 1146.4],
        ["Darwin", 112, 120900, 1714.7],
        ["Hobart", 1357, 205556, 619.5],
        ["Sydney", 2058, 4336374, 1214.8],
        ["Melbourne", 1566, 3806092, 646.9],
        ["Perth", 5386, 1554769, 869.4],
    ]
)
print(table)