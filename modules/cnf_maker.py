from typing import List
import json
import math
import sys
from datetime import datetime
from optilog.modelling import *

def A_table(p:int, subjects:int, classrooms:int, hours:int):
    variable: int = 1
    table: List[List[List[List[List[str]]]]] = []
    for i in range(p):
        table.append([])
        for j in range(subjects):
            table[i].append([])
            for k in range(classrooms):
                table[i][j].append([])
                for d in range(5):
                    table[i][j][k].append([])
                    for _ in range(hours):
                        table[i][j][k][d].append('A' + str(variable))
                        variable += 1
    return (table,variable)

def D_table(p:int, subjects:int, hours:int, variable:int):
    table: List[List[List[List[str]]]] = []
    for i in range(p):
        table.append([])
        for j in range(subjects):
            table[i].append([])
            for d in range(5):
                table[i][j].append([])
                for _ in range(hours):
                    table[i][j][d].append('D' + str(variable))
                    variable += 1
    return table

# obtener el numero total de clausulas para las 4 restricciones
def get_number_clauses(p:int, subjects:int, classrooms:int, hours:int) -> int:
    return 0

# restriccion 0 a CNF
# Un profesor no esta disponible para dar clases en un dia d y hora h si no esta en su disponibilidad
def c0(problem, D: List[List[List[List[str]]]], disp_teachers, start_time: str, end_time: str, n_teachers: int, n_subjects: int, n_hours:int) -> None:
    for p in range(n_teachers):
        for m in range(n_subjects):
            for i, d in enumerate(["lunes", "martes", "miercoles", "jueves", "viernes"]):
                for h in range(n_hours):
                    if d not in disp_teachers[p]["disponibilidad"].keys():
                        problem.add_constr(Not(Bool(D[p][m][i][h])))
                    else:
                        if h not in disp_teachers[p]["disponibilidad"][d] or h==disp_teachers[p]["disponibilidad"][d][-1]:
                            problem.add_constr(Not(Bool(D[p][m][i][h])))

# restriccion 1 a CNF
# Un profesor solo puede impartir una materia a la vez.
def c1(problem, A: List[List[List[List[List[str]]]]], n_teachers: int, n_subjects: int, n_classrooms: int, n_hours:int) -> None:
    for m1 in range(n_subjects):
        for m2 in range(n_subjects):
            if m1 == m2:
                continue
            for p in range(n_teachers):
                for a1 in range(n_classrooms):
                    for a2 in range(n_classrooms):
                        for d in range(5):
                            for h in range(n_hours):
                                problem.add_constr(Or(Not(Bool(A[p][m1][a1][d][h])), Not(Bool(A[p][m2][a2][d][h]))))
    for a1 in range(n_classrooms):
        for a2 in range(n_classrooms):
            if a1 == a2:
                continue
            for p in range(n_teachers):
                for m1 in range(n_subjects):
                    for m2 in range(n_subjects):
                        for d in range(5):
                            for h in range(n_hours):
                                problem.add_constr(Or(Not(Bool(A[p][m1][a1][d][h])), Not(Bool(A[p][m2][a2][d][h]))))


# restriccion 2 a CNF
# En una aula sólo puede impartir una materia a la vez.
def c2(problem, A: List[List[List[List[List[str]]]]], n_teachers: int, n_subjects: int, n_classrooms: int, n_hours:int) -> None:
    for p1 in range(n_teachers):
        for p2 in range(n_teachers):
            if p1 == p2:
                continue
            for m1 in range(n_subjects):
                for m2 in range(n_subjects):
                    for a in range(n_classrooms):
                        for d in range(5):
                            for h in range(n_hours):
                                problem.add_constr(Or(Not(Bool(A[p1][m1][a][d][h])), Not(Bool(A[p2][m2][a][d][h]))))
    for m1 in range(n_subjects):
        for m2 in range(n_subjects):
            if m1 == m2:
                continue
            for p1 in range(n_teachers):
                for p2 in range(n_teachers): 
                    for a in range(n_classrooms):
                        for d in range(5):
                            for h in range(n_hours):
                                problem.add_constr(Or(Not(Bool(A[p1][m1][a][d][h])), Not(Bool(A[p2][m2][a][d][h]))))


# restriccion 3 a CNF
# Un profesor debe estar disponible para impartir una materia en un horario específico.
def c3(problem, A: List[List[List[List[List[str]]]]], D: List[List[List[List[str]]]], n_teachers: int, n_subjects: int, n_classrooms: int, n_hours:int) -> None:
    for p in range(n_teachers):
        for m in range(n_subjects):
            for a in range(n_classrooms):
                for d in range(5):
                    for h in range(n_hours):
                        problem.add_constr(Or(Not(Bool(A[p][m][a][d][h])), Bool(D[p][m][d][h])))


# restriccion 4 a CNF:
# Cada clase dura exactamente dos horas
def c4(problem, A: List[List[List[List[List[str]]]]], n_teachers: int, n_subjects: int, n_classrooms: int, n_hours:int) -> None:
    for p in range(n_teachers):
        for m in range(n_subjects):
            for a in range(n_classrooms):
                for d in range(5):
                    for h1 in range(n_hours):
                        expr = Not(Bool(A[p][m][a][d][h1]))
                        for h2 in range(n_hours):
                            if ((h1 == h2 + 1 or h1 + 1 == h2) and (h1 != h2 + 1 or h1 + 1 != h2)):
                                expr = expr | Bool(A[p][m][a][d][h2])
                        problem.add_constr(expr)

# restriccion 5 a CNF:
# Cada materia se imparte dos veces por semana en el mismo salón designado.
def c5(problem, A: List[List[List[List[List[str]]]]], n_teachers: int, n_subjects: int, n_classrooms: int, n_hours:int) -> None:
    for p in range(n_teachers):
        for m in range(n_subjects):
            Or1 = []
            for a in range(n_classrooms):
                if a == 0:
                    continue
                Or2 = []
                for d1 in range(5):
                    if d1 == 4:
                        continue
                    Or3 = []
                    for h1 in range(n_hours):
                        expr = Bool(A[p][m][a][d1][h1])
                        Or4 = []
                        for d2 in range(5):
                            if d2 <= d1:
                                continue
                            expr2 = Bool(A[p][m][a][d2][h1])
                            for h2 in range(n_hours):
                                if h1 == h2:
                                    continue
                                expr2 = expr2 | Bool(A[p][m][a][d2][h2])
                            Or4.append(expr2)
                        e1 = Or4[0]
                        for idx, e2 in enumerate(Or4):
                            if idx > 0:
                                e1 = e1 | e2
                        expr = expr & e1
                    Or3.append(expr)
                e3 = Or3[0]
                for idx, e4 in enumerate(Or3):
                    if idx > 0:
                        e3 = e3 | e4
                Or2.append(e3)
            e5 = Or2[0]
            for idx, e6 in enumerate(Or2):
                if idx > 0:
                    e5 = e5 | e6
            Or1.append(e5)
    exprf = Or1[0]
    for idx, e7 in enumerate(Or1):
        if idx > 0:
            exprf = exprf & e7
    problem.add_constr(exprf)
    print(exprf)

# traducir restricciones a formato dimacs
def todimacs(start_time: str, end_time: str, p: int, subjects: int, classrooms: int, hours: int, disp_teachers: list, filename: str) -> str:
    # restamos horas menos 1, pues la ultima clase no puede comenzar a la hora final
    hours: int = hours - 1

    # numero de variables en total
    number_of_variables: int = 5*p*subjects*hours*(classrooms+1)

    # creamos la tabla de variables para A_p,m,c,d,h
    x = A_table(p,subjects,classrooms,hours)
    A: List[List[List[List[List[str]]]]] = x[0]
    var: int = x[1]
    # creamos la tabla de variables para D_p,m,d,h 
    D: List[List[List[List[str]]]] = D_table(p,subjects,hours, var)

    # calculamos el numero total de clausulas
    number_of_clauses: int = get_number_clauses(p, subjects, classrooms, hours)
    # nombre del archivo de salida
    outputCointraints: str = filename.name.replace(".json", ".cnf")

    # escribimos las clausulas en el archivo de salida
    f: TextIOWrapper = open(outputCointraints, "w")
    f.write(f"p cnf {number_of_variables} {number_of_clauses}\n")
    f.flush()

    problem = Problem()
    # c0(problem, D, disp_teachers, start_time, end_time, p, subjects, hours)
    # c1(problem, A, p, subjects, classrooms, hours)
    # c2(problem, A, p, subjects, classrooms, hours)
    # c3(problem, A, D, p, subjects, classrooms, hours)
    # c4(problem, A, p, subjects, classrooms, hours)
    c5(problem, A, p, subjects, classrooms, hours)

    return outputCointraints