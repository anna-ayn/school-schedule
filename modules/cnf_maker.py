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
def c0(problem, A: List[List[List[List[List[str]]]]], disp_teachers, n_teachers: int, n_subjects: int, n_classrooms:int, n_hours:int) -> None:
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
# Cada materia se imparte dos veces por semana en el mismo salón designado
def c1(problem, A: List[List[List[List[List[str]]]]], disp_teachers, n_teachers: int, n_subjects: int, n_classrooms: int, n_hours:int) -> None:
    for p in range(n_teachers):
        for m in range(n_subjects):
            if m not in disp_teachers[p]["materias"]:
                continue
            Ors = []
            for a in range(n_classrooms):
                for i1, d1 in enumerate(["lunes", "martes", "miercoles", "jueves", "viernes"]):
                    if d1 not in disp_teachers[p]["disponibilidad"].keys() or d1 == "viernes":
                        continue
                    for h1 in range(n_hours):
                        if h1 not in disp_teachers[p]["disponibilidad"][d1] or h1==disp_teachers[p]["disponibilidad"][d1][-1]:
                            continue
                        for i2, d2 in enumerate(["lunes", "martes", "miercoles", "jueves", "viernes"]):
                            if d2 not in disp_teachers[p]["disponibilidad"].keys() or d2 <= d1:
                                continue
                            for h2 in range(n_hours):
                                if h2 not in disp_teachers[p]["disponibilidad"][d2] or h2==disp_teachers[p]["disponibilidad"][d2][-1]:
                                    continue
                                expr = Bool(A[p][m][a][i1][h1]) & Bool(A[p][m][a][i2][h2])
                                Ors.append(expr)
            if len(Ors) > 0:
                problem.add_constr(Or(Ors))
                                 

# restriccion 2 a CNF
# Dos clases no pueden ocurrir al mismo tiempo para un salon y donde cada clase dura exactamente dos horas.
def c2(problem, A: List[List[List[List[List[str]]]]], disp_teachers, n_teachers: int, n_subjects: int, n_classrooms: int, n_hours:int) -> None:
    for p1 in range(n_teachers):
        for m1 in range(n_subjects):
            if m1 not in disp_teachers[p1]["materias"]:
                continue
            for a in range(n_classrooms):
                for i, d in enumerate(["lunes", "martes", "miercoles", "jueves", "viernes"]):
                    if d not in disp_teachers[p1]["disponibilidad"].keys():
                        continue
                    for h1 in range(n_hours):
                        if h1 not in disp_teachers[p1]["disponibilidad"][d] or h1==disp_teachers[p1]["disponibilidad"][d][-1]:
                            continue
                        for p2 in range(n_teachers):
                            if d not in disp_teachers[p2]["disponibilidad"].keys():
                                continue
                            for m2 in range(n_subjects):
                                if m2 not in disp_teachers[p2]["materias"]:
                                    continue
                                if p1 == p2 and m1 == m2:
                                    continue
                                for h2 in range(n_hours):
                                    if h2 not in disp_teachers[p2]["disponibilidad"][d] or h2==disp_teachers[p2]["disponibilidad"][d][-1]:
                                        continue
                                    if h2 != h1 and h2 != h1 + 1:
                                        continue 
                                    expr = Or(Not(Bool(A[p1][m1][a][i][h1])), Not(Bool(A[p2][m2][a][i][h2])))
                                    problem.add_constr(expr)
# restriccion 3 a CNF:
# Un profesor solo puede impartir una materia a la vez
def c3(problem, A: List[List[List[List[List[str]]]]], disp_teachers, n_teachers: int, n_subjects: int, n_classrooms: int, n_hours:int) -> None:
    for p in range(n_teachers):
        for m1 in range(n_subjects):
            if m1 not in disp_teachers[p]["materias"]:
                continue
            for a1 in range(n_classrooms):
                for i, d in enumerate(["lunes", "martes", "miercoles", "jueves", "viernes"]):
                    if d not in disp_teachers[p]["disponibilidad"].keys():
                        continue
                    for h in range(n_hours):
                        if h not in disp_teachers[p]["disponibilidad"][d] or h==disp_teachers[p]["disponibilidad"][d][-1]:
                            continue
                        for m2 in range(n_subjects):
                            if m2 not in disp_teachers[p]["materias"]:
                                continue
                            for a2 in range(n_classrooms):
                                if m1 == m2 and a1 == a2:
                                    continue
                                expr = Or(Not(Bool(A[p][m1][a1][i][h])), Not(Bool(A[p][m2][a2][i][h])))
                                problem.add_constr(expr)
                                if h + 1 != n_hours:
                                    expr = Or(Not(Bool(A[p][m1][a1][i][h])), Not(Bool(A[p][m2][a2][i][h + 1])))
                                    problem.add_constr(expr)

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
    t0 = threading.Thread(target=c0, args=(problem, A, disp_teachers, p, subjects, classrooms,hours))
    threads.append(t0)

    t1 = threading.Thread(target=c1, args=(problem, A, disp_teachers, p, subjects, classrooms, hours))
    threads.append(t1)

    t2 = threading.Thread(target=c2, args=(problem, A, disp_teachers, p, subjects, classrooms, hours))
    threads.append(t2)

    t3 = threading.Thread(target=c3, args=(problem, A, disp_teachers, p, subjects, classrooms, hours))
    threads.append(t3)

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
    if len(interpretation) > 0:
        model = []

        for e in interpretation:
            model.append(str(e))
        
        i = 0
        for e in model:
            if e[0] == "~":
                i = i + 1
    else:
        print("No model found")
    return (outputCointraints, cnf)