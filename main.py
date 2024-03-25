import json
import math
import sys
import os
from typing import List
from datetime import datetime
from modules.cnf_maker import *
from modules.time_converter import *

# Colores en la terminal
class Colors:
    HEADER = '\033[0;104m' 
    OKBLUE = '\033[1;94m' 
    OKGREEN = '\033[1;92m' 
    WARNING = '\033[1;93m'
    FAIL = '\033[1;91m' 
    END = '\033[0m'
    UNDERLINE_GREEN = '\033[42m'

def main():
    solved: bool = True
    total_time_start: datetime = datetime.now()
    print(f"\n👋 {Colors.HEADER}¡Bienvenido al Planificador de Horarios de Asignaturas!{Colors.END}\n")

    # Obtener el archivo JSON
    file: str = sys.argv[1]
    print(f"Abriendo el archivo {Colors.UNDERLINE_GREEN}{file}{Colors.END}...")

    # intentar abrir el archivo JSON
    try:
        with open(file, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"{Colors.FAIL}ERROR:{Colors.END} No existe el archivo {file}.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(
            f"{Colors.FAIL}ERROR:{Colors.END} Hay un problema con la forma en que formatea los datos JSON en el archivo {file}."
        )
        sys.exit(1)

    # guardar los datos en variables
    # nombre del colegio
    t_name: str = data["colegio"]
    # disponibilidad de profesores
    disp_teachers = data["profesores"]
    # salones
    classrooms: List[str] = data["aulas"]
    # horas de inicio y fin de las clases
    start_time: str = data["hora_inicio"]
    end_time: str = data["hora_final"]

    # guardar cada nombre de profesor en una lista
    teachers: List[str] = [teacher["nombre"] for teacher in disp_teachers]
    # guardar cada materia de profesor en un conjunto
    subjects: set[str] = {subject for teacher in disp_teachers for subject in teacher["materias"]}

    # imprimir los datos
    print(f"\n{Colors.OKBLUE}Colegio:{Colors.END} {t_name}")
    print(f"{Colors.OKBLUE}Profesores:{Colors.END} {teachers}")
    print(f"{Colors.OKBLUE}Materias:{Colors.END} {subjects}")
    print(f"{Colors.OKBLUE}Aulas:{Colors.END} {classrooms}")
    print(f"{Colors.OKBLUE}Horario de inicio del colegio:{Colors.END} {start_time}")
    print(f"{Colors.OKBLUE}Horario de cierre del colegio:{Colors.END} {end_time}")

    # cantidad de profesores
    n_teachers: int = len(teachers)
    # cantidad de materias
    n_subjects: int = len(subjects)
    # cantidad de aulas
    n_classrooms: int = len(classrooms)
    # cantidad de horas de clases posibles por dia
    n_hours: int = diff_hours(start_time, end_time)

    # Verificar las siguientes condiciones
    if not start_time.endswith(":00.000"):
        print(f"{Colors.FAIL}ERROR:{Colors.END} El horario de inicio del colegio debe ser una hora en punto.")
        solved = False

    if not end_time.endswith(":00.000"):
        print(f"{Colors.FAIL}ERROR:{Colors.END} El horario de cierre del colegio debe ser una hora en punto.")
        solved = False
    
    # Verificar las horas disponibles por día de cada profesor
    for teacher in disp_teachers:
        if len(teacher["disponibilidad"]) < 1:
            print(f"{Colors.FAIL}ERROR:{Colors.END} El prof. {teacher['nombre']} debe estar disponible para dar clases al menos un dia de cada semana.")
            solved = False
        for d in teacher["disponibilidad"].keys():
            if d != "lunes" and d != "martes" and d != "miercoles" and d != "jueves" and d != "viernes":
                print(f"{Colors.FAIL}ERROR:{Colors.END} El prof. {teacher['nombre']} solo puede estar disponible para dar clases de lunes a viernes.")
                solved = False
        i = 0
        htotal = 0
        for h in teacher["disponibilidad"].values():
            st = h[0]
            et = h[1]
            if not st.endswith(":00.000"):
                print(f"{Colors.FAIL}ERROR:{Colors.END} La hora de inicio de disponibilidad de un profesor debe ser una hora en punto.")
                solved = False
            if not et.endswith(":00.000"):
                print(f"{Colors.FAIL}ERROR:{Colors.END} La hora final de disponibilidad de un profesor debe ser una hora en punto.")
                solved = False

            d = list(teacher["disponibilidad"].keys())
            # verificar que haya al menos dos horas disponibles
            diff = diff_hours(st, et)
            if diff < 2:
                print(f"{Colors.FAIL}ERROR:{Colors.END} El prof. {teacher['nombre']} debe estar disponible para dar clases por lo menos dos horas en los dias {d[i]}")
                solved = False
            htotal = htotal + (diff//2)
            i += 1
        # verificar que la cantidad de horas disponibles de un profesor alcance para la cantidad de materias que puede dar
        if htotal < len(teacher["materias"]):
            print(f"{Colors.FAIL}ERROR:{Colors.END} El prof. {teacher['nombre']} no tiene suficientes horas disponibles para dar todas las materias que el desea dar.")
            solved = False

    if solved:
        print(f"\n{Colors.OKGREEN}¡Todas las condiciones se cumplen!{Colors.END}")
    else:
        exit(1)

    return


if __name__ == "__main__":
    main()