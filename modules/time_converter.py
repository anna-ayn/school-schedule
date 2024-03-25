from datetime import datetime, time, timedelta
from typing import List

def diff_hours(start_time: str, end_time: str) -> int:
    # Cantidad de horas que durara el torneo
    hora1: time = datetime.strptime(start_time, "%H:%M:%S.%f").time()
    hora2: time = datetime.strptime(end_time, "%H:%M:%S.%f").time()
    # Calcular la diferencia en horas
    return int((
        datetime.combine(datetime.min, hora2) - datetime.combine(datetime.min, hora1)
    ).total_seconds() // 3600)


def calc_day(date: str, days: int) -> str:
    """
    Esta funcion toma una fecha y le suma un numero de dias
    ### Parametros
    - date: str - Fecha en formato "YYYY-MM-DD"
    - days: int - Cantidad de dias a sumar
    ### Retorna
    - str - Fecha en formato "YYYY-MM-DD"
    """
    return (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")

def calc_time(start_time: str, hours: int) -> str:
    """
    Esta funcion toma una hora y le suma un numero de horas
    ### Parametros
    - start_time: str - Hora en formato "HH:MM:SS"
    - hours: int - Cantidad de horas a sumar
    ### Retorna
    - str - Hora en formato "HH:MM:SS"
    """
    return (datetime.combine(datetime.min, datetime.strptime(start_time, "%H:%M:%S.%f").time()) + timedelta(hours=hours)).strftime("%H:%M:%S.%f")