from typing import List, Dict
from prettytable.colortable import ColorTable, Themes, Theme

# Clase para la tabla de colores
tema_1 = Theme(
    vertical_color="93", 
    horizontal_color="93", 
    junction_color="92", 
    vertical_char="|", 
    horizontal_char="=", 
    junction_char="*"
)

def imprimir_disponibilidad(disp_teachers: List[Dict[str, str]]) -> None:
    # Crear la tabla de colores
    table = ColorTable(theme=tema_1)
    field_names: List[str] = ["Nombre", "Materias", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    # Crear la fila de cabecera
    table.field_names = field_names
    # Crear la fila de datos
    for teacher in disp_teachers:
        # Crear la fila de datos
        row = [teacher["nombre"], ", ".join(teacher["materias"])]
        # Crear la fila de disponibilidad
        for day in ["lunes", "martes", "miercoles", "jueves", "viernes"]:
            if day in teacher["disponibilidad"]:
                inicio: str = ":".join(teacher["disponibilidad"][day][0].split(":")[:2])
                fin: str = ":".join(teacher["disponibilidad"][day][1].split(":")[:2])
                row.append(f"{inicio} - {fin}")
            else:
                row.append("No disponible")
        # Agregar la fila a la tabla
        table.add_row(row)
    print("\033[1;94mProfesores:\033[0m")
    print(table)