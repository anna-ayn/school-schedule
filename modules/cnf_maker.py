from typing import List
import json
import math
import sys
from datetime import datetime

# enumeraremos las variables de 1 a 2*n*days*hours
# y lo almacenaremos en una tabla de 4 dimensiones
# cada columna corresponde al numero del participante, el tipo de juego (local o visitante), el dia y la hora
def table_variables(n: int, days: int, hours: int) -> List[List[List[List[int]]]]:
    variable: int = 1
    table: List[List[List[List[int]]]] = []
    for i in range(n):
        table.append([])
        for j in range(n):
            table[i].append([])
            for k in range(days):
                table[i][j].append([])
                for _ in range(hours):
                    table[i][j][k].append(variable)
                    variable += 1
    return table


# obtener el numero total de clausulas para las 4 restricciones
def get_number_clauses(n: int, days: int, hours: int) -> int:
    c1: int = n * (n - 1)
    c2: int = int(n * (n - 1) * days * hours * (n - (1/(n-1))) * (n - 1) * (2 - (1 / hours)))
    c3: int = 4 * n * (n - 1) * n * days * hours * (hours - 1)
    c4: int = 2 * n * (n - 1) * n * (days - 1) * hours * hours
    c5: int = n * days * hours
    return c1 + c2 + c3 + c4 + c5


# restriccion 1 a CNF
# todos los participantes deben jugar dos veces con cada uno de los otros participantes
# una como "visitantes" y la otra como "locales".
def c1(filename: str, table: List[List[List[List[int]]]], n: int, days: int, hours: int) -> None:
    file: TextIOWrapper = open(filename, "a")
    for loc in range(n):
        for vis in range(n):
            if loc == vis:
                continue
            for d in range(days):
                for h in range(hours):
                    # se imprime clausula
                    file.write(f"{table[loc][vis][d][h]} ")
            file.write(f"0\n")
    file.flush()


# restriccion 2 a CNF
# Dos juegos no pueden ocurrir al mismo tiempo
def c2(filename: str, table: List[List[List[List[int]]]], n: int, days: int, hours: int) -> None:
    file: TextIOWrapper = open(filename, "a")
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
                
            for d in range(days):
                for h1 in range(hours):
                    J_abdh1 = table[a][b][d][h1]
                    
                    for x in range(n):
                        for y in range(n):
                            if x == y or (a == x and b == y):
                                continue
                            
                            for h2 in range(hours):
                                if h1 != h2 and h2 != h1 + 1:
                                    continue
                                J_xydh2: int = table[x][y][d][h2]
                                
                                file.write(f"{-J_abdh1} {-J_xydh2} 0\n")
    file.flush()


# restriccion 3 a CNF
# Un participante puede jugar a lo sumo una vez por dia
def c3(filename: str, table: List[List[List[List[int]]]], n: int, days: int, hours: int) -> None:
    file: TextIOWrapper = open(filename, "a")

    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            for c in range(n):
                for d in range(days):
                    for h1 in range(hours):
                        for h2 in range(hours):
                            if h1 == h2:
                                continue

                            J_abdh1: int = table[a][b][d][h1]
                            
                            file.write(f"{-J_abdh1} {-table[c][a][d][h2]} 0\n")
                            file.write(f"{-J_abdh1} {-table[a][c][d][h2]} 0\n")
                            file.write(f"{-J_abdh1} {-table[b][c][d][h2]} 0\n")
                            file.write(f"{-J_abdh1} {-table[c][b][d][h2]} 0\n")
    file.flush()


# restriccion 4 a CNF:
# Un participante no puede jugar de "visitante" en dos dias consecutivos, ni de "local" dos dias seguidos
def c4(filename: str, table: List[List[List[List[int]]]], n: int, days: int, hours: int) -> None:
    file: TextIOWrapper = open(filename, "a")

    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            for c in range(n):
                for d in range(days-1):
                    for h1 in range(hours):
                        for h2 in range(hours):
                            J_abdh1: int = table[a][b][d][h1]
                            
                            file.write(f"{-J_abdh1} {-table[a][c][d+1][h2]} 0\n")
                            file.write(f"{-J_abdh1} {-table[c][b][d+1][h2]} 0\n")
    file.flush()


# restriccion 5 a CNF:
# Un participante no puede jugar contra si mismo
def c5(filename: str, table: List[List[List[List[int]]]], n: int, days: int, hours: int) -> None:
    file: TextIOWrapper = open(filename, "a")

    for a in range(n):
        for d in range(days):
            for h in range(hours):
                
                file.write(f"{-table[a][a][d][h]} 0\n")
    file.flush()


# traducir restricciones a formato dimacs
def todimacs(n: int, days: int, hours: int, filename: str) -> str:
    # restamos horas menos 1, pues el ultimo partido de un dia no puede comenzar a la hora final
    hours: int = hours - 1

    # numero de variables en total
    number_of_variables: int = n * n * days * hours
    # creamos la tabla de variables
    table: List[List[List[List[int]]]] = table_variables(n, days, hours)

    # calculamos el numero total de clausulas
    number_of_clauses: int = get_number_clauses(n, days, hours)
    # nombre del archivo de salida
    outputCointraints: str = filename.name.replace(".json", ".cnf")

    # escribimos las clausulas en el archivo de salida
    f: TextIOWrapper = open(outputCointraints, "w")
    f.write(f"p cnf {number_of_variables} {number_of_clauses}\n")
    f.flush()
    c1(outputCointraints, table, n, days, hours)
    c2(outputCointraints, table, n, days, hours)
    c3(outputCointraints, table, n, days, hours)
    c4(outputCointraints, table, n, days, hours)
    c5(outputCointraints, table, n, days, hours)

    return outputCointraints