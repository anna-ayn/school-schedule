import json
import math
import sys
import os
from typing import List
from datetime import datetime
from optilog.solvers.sat import *
from modules.cnf_maker import *
from modules.time_converter import *
from modules.tables_out import *
from modules.pdf_creator import create_pdf
from optilog.modelling import *

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
    print(f"{Colors.OKBLUE}Materias:{Colors.END} {subjects}")
    print(f"{Colors.OKBLUE}Aulas:{Colors.END} {classrooms}")
    print(f"{Colors.OKBLUE}Horario de inicio del colegio:{Colors.END} {start_time}")
    print(f"{Colors.OKBLUE}Horario de cierre del colegio:{Colors.END} {end_time}")
    imprimir_disponibilidad(disp_teachers)

    # cantidad de profesores
    n_teachers: int = len(teachers)
    # cantidad de materias
    n_subjects: int = len(subjects)
    # cantidad de aulas
    n_classrooms: int = len(classrooms)
    # cantidad de horas abiertas del colegio
    n_hours: int = diff_hours(start_time, end_time)

    # Verificar las siguientes condiciones
    if not start_time.endswith(":00.000"):
        print(f"{Colors.FAIL}ERROR:{Colors.END} El horario de inicio del colegio debe ser una hora en punto.")
        solved = False

    if not end_time.endswith(":00.000"):
        print(f"{Colors.FAIL}ERROR:{Colors.END} El horario de cierre del colegio debe ser una hora en punto.")
        solved = False
    
    # Verificar las horas disponibles por día de cada profesor
    for t, teacher in enumerate(disp_teachers):
        # enumerar las materias segun subjects
        for i, s in enumerate(subjects):
            for j, m in enumerate(teacher["materias"]):
                if s == m:
                    disp_teachers[t]["materias"][j] = i

        if len(teacher["disponibilidad"]) < 2:
            print(f"{Colors.FAIL}ERROR:{Colors.END} El prof. {teacher['nombre']} debe estar disponible para dar clases al menos dos dias de cada semana.")
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
            # enumerar las horas disponibles del profesor dentro del horario del colegio
            hours_start = diff_hours(start_time, st)
            hours_end = diff_hours(start_time, et)
            available_hours = list(range(hours_start, hours_end))
            available_hours = [h for h in available_hours if h >= 0 and h < n_hours]
            disp_teachers[t]["disponibilidad"][d[i]] = available_hours
            # verificar que tenga al menos dos horas disponibles en los dias que pueda ir al colegio
            if len(available_hours) <= 1:
                print(f"{Colors.FAIL}ERROR:{Colors.END} El prof. {teacher['nombre']} debe estar disponible para dar clases por lo menos dos horas en los dias {d[i]} dentro del horario del colegio.")
                solved = False
            htotal = htotal + (len(available_hours)//2)
            i += 1
        # verificar que la cantidad de horas disponibles de un profesor alcance para la cantidad de materias que puede dar
        if htotal < len(teacher["materias"]):
            print(f"{Colors.FAIL}ERROR:{Colors.END} El prof. {teacher['nombre']} no tiene suficientes horas disponibles para dar todas las materias que el desea dar.")
            solved = False

    time_start: datetime = datetime.now()
    cnf_file: str = None
    cnf = None
    if solved:
        print(f"\n{Colors.OKGREEN}¡Todas las condiciones se cumplen!{Colors.END}")
        cnf_file, cnf = todimacs(start_time, end_time, n_teachers, n_subjects, n_classrooms, n_hours, disp_teachers, file)
        print(F"Archivo de restricciones en formato DIMACS creado {Colors.OKGREEN}exitosamente!{Colors.END}")

    time_end: datetime = datetime.now()
    time_taken_1: str = str(time_end - time_start)
    print(f"\n⌛ Tiempo que tomo en convertir las restricciones en formato DIMACS: {Colors.OKBLUE}{time_taken_1}{Colors.END}")
    time_start = datetime.now()

    # Crear el solver
    solver: Glucose41 = Glucose41()
    if cnf_file is not None:
        solver.load_cnf(cnf_file)

    model: List[int] = []

    # Resolver el problema con Glucose
    glucose_sat: bool = False
    if solved and solver.solve():
        model = solver.model()
        solved = any(x >= 0 for x in model) and len(model) > 0
        if solved:
            print(f"\n{Colors.OKGREEN}¡Problema resuelto exitosamente con Glucose!{Colors.END}")
            glucose_sat = True
    else:
        solved = False
    time_end = datetime.now()
    time_taken_2: str = str(time_end - time_start)
    print(f"\n⌛ Tiempo que tomo en resolver el problema con Glucose: {Colors.OKBLUE}{time_taken_2}{Colors.END}")

    # Resolver el problema con Cadical 1.0.3
    cadical_sat: bool = False
    solver2: Cadical = Cadical()
    if solved and solver2.solve():
        model = solver2.model()
        solved = any(x >= 0 for x in model) and len(model) > 0
        if solved:
            print(f"\n{Colors.OKGREEN}¡Problema resuelto exitosamente con Cadical 1.0.3!{Colors.END}")
            cadical_sat = True
    else:
        solved = False
    time_end = datetime.now()
    time_taken_2: str = str(time_end - time_start)
    print(f"\n⌛ Tiempo que tomo en resolver el problema con Cadical 1.0.3: {Colors.OKBLUE}{time_taken_2}{Colors.END}")

    # Resolver el problema con Lingeling 2018
    lingeling_sat: bool = False 
    solver: Lingeling18 = Lingeling18()
    if solved and solver.solve():
        model = solver.model()
        solved = any(x >= 0 for x in model) and len(model) > 0
        if solved:
            print(f"\n{Colors.OKGREEN}¡Problema resuelto exitosamente con Lingeling 2018!{Colors.END}")
            cadical_sat = True
    else:
        solved = False
    time_end = datetime.now()
    time_taken_2: str = str(time_end - time_start)
    print(f"\n⌛ Tiempo que tomo en resolver el problema con Lingeling 2018: {Colors.OKBLUE}{time_taken_2}{Colors.END}")

    

    # Resolver el problema con Kissat
    kissat_path: str = "./kissat-rel-3.1.1/build/kissat"
    kissat_time_start: datetime = datetime.now()
    kissat_sat: bool = False
    if solved and os.path.exists(kissat_path):
        # Ejecutar el comando `kissat_path cnf_file` y guardar la salida estandar como un string
        output: str = os.popen(f"{kissat_path} {cnf_file}").read()
        if "s SATISFIABLE" in output:
            kissat_sat = True
            print(f"\n{Colors.OKGREEN}¡Problema resuelto exitosamente con Kissat!{Colors.END}")
        else:
            print(f"{Colors.FAIL}ERROR:{Colors.END} No se pudo encontrar una solución con Kissat.")
    elif not os.path.exists(kissat_path):
        print(f"{Colors.FAIL}ERROR:{Colors.END} No se pudo encontrar el ejecutable de Kissat en la ruta {kissat_path}.")
    kissat_time_end: datetime = datetime.now()
    kissat_time_taken: str = str(kissat_time_end - kissat_time_start)
    print(f"\n⌛ Tiempo que tomo en resolver el problema con Kissat: {Colors.OKBLUE}{kissat_time_taken}{Colors.END}")

    # Resolver el problema con Rsat
    rsat_path: str = "./rsat/rsat.sh"
    rsat_time_start: datetime = datetime.now()
    rsat_sat: bool = False
    if solved and os.path.exists(rsat_path):
        # Ejecutar el comando `rsat_path cnf_file` y guardar la salida estandar como un string
        output: str = os.popen(f"{rsat_path} {cnf_file}").read()
        if "s SATISFIABLE" in output:
            rsat_sat = True
            print(f"\n{Colors.OKGREEN}¡Problema resuelto exitosamente con Rsat!{Colors.END}")
        else:
            print(f"{Colors.FAIL}ERROR:{Colors.END} No se pudo encontrar una solución con Rsat.")
    elif not os.path.exists(rsat_path):
        print(f"{Colors.FAIL}ERROR:{Colors.END} No se pudo encontrar el ejecutable de Rsat en la ruta {rsat_path}.")
    rsat_time_end: datetime = datetime.now()
    rsat_time_taken: str = str(rsat_time_end - rsat_time_start)
    print(f"\n⌛ Tiempo que tomo en resolver el problema con Rsat: {Colors.OKBLUE}{rsat_time_taken}{Colors.END}\n")

    if not solved:
        print(f"{Colors.FAIL}ERROR:{Colors.END} No se pudo encontrar una solución.")
    else:
        interpretation = [str(x) for x in cnf.decode_dimacs(model)]
        school: str = t_name.replace(" ", "_").lower()
        pdf_name: str = f"oferta_{school}.pdf"
        # Si existe un archivo PDF con el mismo nombre, se elimina
        if os.path.exists(pdf_name):
            os.remove(pdf_name)
        create_pdf(interpretation, disp_teachers, list(subjects), classrooms, n_hours, start_time, pdf_name)
        print(f"📄 Archivo PDF creado {Colors.OKGREEN}exitosamente!{Colors.END}")
        print(f"Archivo PDF: {Colors.UNDERLINE_GREEN}{pdf_name}{Colors.END}")

    if cnf_file is not None:
        # Eliminar el archivo de restricciones en formato DIMACS
        os.remove(cnf_file)

    total_time_end: datetime = datetime.now()
    total_time_taken: str = str(total_time_end - total_time_start)
    print(f"\n⏳ Tiempo total que tomo el programa: {Colors.OKBLUE}{total_time_taken}{Colors.END}")
    print(f"\n👋 {Colors.HEADER}¡Gracias por usar el Planificador de Horarios de Asignaturas!{Colors.END}\n")

    # Guardamos los tiempos en el archivo times.txt
    # El formato es: <archivo_json>\t<tiempo_convertir_restricciones>\t<tiempo_glucose>\t<tiempo_kissat>\t<tiempo_rsat>\t<tiempo_total>
    with open("times.txt", "a") as file:
        file.write(f"{sys.argv[1]}\t{time_taken_1}\t{time_taken_2} {'SAT' if glucose_sat else 'UNSAT'}\t{kissat_time_taken} {'SAT' if kissat_sat else 'UNSAT'}\t{rsat_time_taken} {'SAT' if rsat_sat else 'UNSAT'}\t{total_time_taken}\n")

    return


if __name__ == "__main__":
    main()