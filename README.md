# School Schedule

Este proyecto tiene como objetivo resolver el problema de asignar materias a profesores de una escuela. Para ello, se utiliza el lenguaje de programación Python, en donde usando la librería `optilog` se puede resolver el problema de asignación de materias a profesores de manera óptima. Ademas, con el fin de evaluar la eficiencia de la solución, se utiliza el solver `Rsat` y `Kissat` para resolver el problema de satisfacción de restricciones.

## Uso

Primeramente, es necesario instalar las dependencias del proyecto. Para ello, se puede ejecutar el siguiente comando:

```bash
pip install -r requirements.txt # o pip3 si es necesario
```

Posteriormente, es necesario compilar los solvers de `Rsat` y `Kissat`. Para ello, se deben ejecutar los siguientes comandos:

```bash
tar -xzf rsat.tar.gz # Opcional
tar -xzf kissat.tar.gz && cd kissat-rel-3.1.1 && ./configure && make && cd ..
```

Finalmente, se puede ejecutar el programa con el siguiente comando:

```bash
./runner.sh <archivo_de_entrada>
```

Donde `<archivo_de_entrada>` es el archivo que contiene la información de las materias y los profesores. Un ejemplo de este archivo es el siguiente:

<!-- TODO: Poner ejemplo -->
```json
{
    "colegio": "Colegio 1",
    "profesores": [
    {
      "nombre": "Pedro",
      "materias": ["Matemáticas", "Física"],
      "disponibilidad": {
        "lunes": ["8:00", "10:00"],
        "martes": ["10:00", "12:00"]
      }
    },
    {
      "nombre": "Maria",
      "materias": ["Historia", "Literatura"],
      "disponibilidad": {
        "lunes": ["8:00", "10:00"],
        "martes": ["8:00", "10:00"]
      }
    }
  ],
  "aulas": ["Aula 1", "Aula 2", "Aula 3"],
  "hora_inicio": "07:00:00.000",
  "hora_final": "19:00:00.000"
}
```
Finalmente, el programa generará un archivo de salida con la información de las materias asignadas a los profesores. Este archivo se llamará `oferta_<colegio>.pdf`

> [!NOTE]
> Es opcional instalar las librerias de Python o compilar los solvers, el script `runner.sh` se encarga de instalarlas, descomprimir y compilar lo necesario para le ejecución del programa.