from typing import List
import json
import math
import sys
from datetime import datetime
from optilog.modelling import *
from contextlib import redirect_stdout
import threading
from optilog.solvers.sat import Glucose41


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
    return table


# restriccion 0 a CNF
# Un profesor no esta disponible para dar clases en un dia d y hora h si no esta en su disponibilidad
# y tampoco puede dar una materia si no esta en su disponibilidad
def c0(problem, A: List[List[List[List[List[str]]]]], disp_teachers, start_time: str, end_time: str, n_teachers: int, n_subjects: int, n_classrooms:int, n_hours:int) -> None:
    for p in range(n_teachers):
        for m in range(n_subjects):
            if m not in disp_teachers[p]["materias"]:
                for a in range(n_classrooms):
                    for d in range(5):
                        for h in range(n_hours):
                            problem.add_constr(Not(Bool(A[p][m][a][d][h])))
            else:
                for i, d in enumerate(["lunes", "martes", "miercoles", "jueves", "viernes"]):
                    for h in range(n_hours):
                        if d not in disp_teachers[p]["disponibilidad"].keys():
                            for a in range(n_classrooms):
                                problem.add_constr(Not(Bool(A[p][m][a][i][h])))
                        else:
                            if h not in disp_teachers[p]["disponibilidad"][d] or h==disp_teachers[p]["disponibilidad"][d][-1]:
                                for a in range(n_classrooms):
                                    problem.add_constr(Not(Bool(A[p][m][a][i][h])))

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


# restriccion 4 a CNF:
# Cada clase dura exactamente dos horas
def c3(problem, A: List[List[List[List[List[str]]]]], n_teachers: int, n_subjects: int, n_classrooms: int, n_hours:int) -> None:
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
def c4(problem, A: List[List[List[List[List[str]]]]], n_teachers: int, n_subjects: int, n_classrooms: int, n_hours:int) -> None:
    for p in range(n_teachers):
        for m in range(n_subjects):
            Ors = []
            for a in range(n_classrooms):
                if a == 0:
                    continue
                for d1 in range(5):
                    if d1 == 4:
                        continue
                    for h1 in range(n_hours):
                        for d2 in range(5):
                            if d2 <= d1:
                                continue
                            for h2 in range(n_hours):
                                if h1 == h2:
                                    continue
                                expr = Bool(A[p][m][a][d1][h1]) & Bool(A[p][m][a][d2][h2])
                                Ors.append(expr)
            problem.add_constr(Or(Ors))

# restriccion 6 a CNF:
# Un profesor no puede impartir una misma materia más de una vez en un mismo dia.
def c5(problem, A: List[List[List[List[List[str]]]]], n_teachers: int, n_subjects: int, n_classrooms: int, n_hours:int) -> None:
    for p in range(n_teachers):
        for m in range(n_subjects):
            for a in range(n_classrooms):
                for d in range(5):
                    for h1 in range(n_hours):
                        expr = Bool(A[p][m][a][d][h1])
                        for h2 in range(n_hours):
                            if h2 == h1 and h2 == h1+1:
                                continue
                            problem.add_constr(expr | Not(Bool(A[p][m][a][d][h2])))


# traducir restricciones a formato dimacs
def todimacs(start_time: str, end_time: str, p: int, subjects: int, classrooms: int, hours: int, disp_teachers: list, filename: str) -> str:
    # restamos horas menos 1, pues la ultima clase no puede comenzar a la hora final
    hours: int = hours - 1

    # creamos la tabla de variables para A_p,m,c,d,h
    A: List[List[List[List[List[str]]]]] = A_table(p,subjects,classrooms,hours)

    # nombre del archivo de salida DIMACS
    outputCointraints: str = filename.name.replace(".json", ".cnf")

    problem = Problem()
    # Create a list to hold the threads
    threads = []

    # repartir el trabajo de modelar las restricciones entre los hilos
    t0 = threading.Thread(target=c0, args=(problem, A, disp_teachers, start_time, end_time, p, subjects, classrooms,hours))
    threads.append(t0)

    t1 = threading.Thread(target=c1, args=(problem, A, p, subjects, classrooms, hours))
    threads.append(t1)

    #t2 = threading.Thread(target=c2, args=(problem, A, p, subjects, classrooms, hours))
    #threads.append(t2)

    #t3 = threading.Thread(target=c3, args=(problem, A, p, subjects, classrooms, hours))
    #threads.append(t3)

    #t4 = threading.Thread(target=c4, args=(problem, A, p, subjects, classrooms, hours))
    #threads.append(t4)

    #t5 = threading.Thread(target=c5, args=(problem, A, p, subjects, classrooms, hours))
    #threads.append(t5)

    # iniciar los hilos
    for thread in threads:
        thread.start()

    # esperar a que los hilos terminen
    for thread in threads:
        thread.join()
    
    # convertir el problema a formato DIMACS CNF
    cnf = problem.to_cnf_dimacs()
    with open(outputCointraints, 'w') as f:
        with redirect_stdout(f):
            print(cnf)

    s = Glucose41()
    s.add_clauses(cnf.clauses)
    s.solve()
    interpretation = cnf.decode_dimacs(s.model())

    model = []
    for e in interpretation:
        if isinstance(e, Not):
            continue
        model.append(str(e))
    
    
    for p in range(p):
        for m in range(subjects):
            for a in range(classrooms):
                for d in range(5):
                    for h in range(hours):
                        if '~' + A[p][m][a][d][h] in model:
                            continue
                        print(f"Variable is true for teacher {p}, subject {m}, classroom {a}, day {d}, and hour {h}")


    return (outputCointraints, cnf)