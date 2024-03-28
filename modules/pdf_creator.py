import copy
from typing import List
import fitz
from modules.cnf_maker import A_table
from modules.time_converter import calc_time

def html_code(offered_subjects: List[dict]) -> str:
    text = """
    <style>
    body {
        font-family: sans-serif;
        font-size: 12px;
        width: 100%;
    }

    td,
    th {
        border: 1px solid black;
        border-right: none;
        border-bottom: none;
        padding: 5px;
        text-align: center;
        width: 100%;
    }

    table {
        width: 100%;
        border-right: 1px solid black;
        border-bottom: 1px solid black;
        border-spacing: 0;
    }
    </style>

    <body>
    <h1>Oferta de Materias</h1>
    <table>
        <tr>
        <th>Profesor</th>
        <th>Materia</th>
        <th>Salon</th>
        <th>Lunes</th>
        <th>Martes</th>
        <th>Miercoles</th>
        <th>Jueves</th>
        <th>Viernes</th>
        </tr>
    """

    for subject in offered_subjects:
        monday: str = subject["lunes"] if "lunes" in subject else "-"
        tuesday: str = subject["martes"] if "martes" in subject else "-"
        wednesday: str = subject["miercoles"] if "miercoles" in subject else "-"
        thursday: str = subject["jueves"] if "jueves" in subject else "-"
        friday: str = subject["viernes"] if "viernes" in subject else "-"

        text += f"""
        <tr>
            <td>{subject["profesor"]}</td>
            <td>{subject["materia"]}</td>
            <td>{subject["aula"]}</td>
            <td>{monday}</td>
            <td>{tuesday}</td>
            <td>{wednesday}</td>
            <td>{thursday}</td>
            <td>{friday}</td>
        </tr>
        """

    text += "</table></body>"
    return text

def sort_subjects(offered_subjects: List[dict], disp_teachers: List[dict]) -> List[dict]:
    sub_copy: List[dict] = copy.deepcopy(offered_subjects)
    sorted_subjects: List[dict] = []
    while len(sub_copy) > 0:
        class_d: dict = sub_copy.pop()
        e: dict = {
            "profesor": class_d["profesor"],
            "materia": class_d["materia"],
            "aula": class_d["aula"],
            class_d["dia"]: class_d["hora"].replace(":00.000000", "")
        }
        while(any([e["profesor"] == s["profesor"] and e["materia"] == s["materia"] for s in sub_copy])):
            i: int = 0
            for c in sub_copy:
                if e["profesor"] == c["profesor"] and e["materia"] == c["materia"]:
                    e[c["dia"]] = c["hora"].replace(":00.000000", "")
                    sub_copy.pop(i)
                    break
                i += 1
        sorted_subjects.append(e)
    return sorted_subjects

def decode_model(model: List[str], disp_teachers: List[dict], subjects: List[str], classrooms: List[str], hours: int, start_time: str) -> List[dict]:
    offered_subjects: List[dict] = []
    A: List[str] = A_table(len(disp_teachers), len(subjects), len(classrooms), hours-1)
    dias: List[str] = ["lunes", "martes", "miercoles", "jueves", "viernes"]
    for p in range(len(disp_teachers)):
        for m in range(len(subjects)):
            for a in range(len(classrooms)):
                for d in range(5):
                    for h in range(hours-1):
                        if "~" + A[p][m][a][d][h] in model:
                            continue
                        time_start: str = calc_time(start_time, h)
                        end_time: str = calc_time(start_time, h+2)
                        offered_subjects.append({
                            "profesor": disp_teachers[p]["nombre"],
                            "materia": subjects[m],
                            "aula": classrooms[a],
                            "dia": dias[d],
                            "hora": f"{time_start} - {end_time}"
                        })
    return sort_subjects(offered_subjects, disp_teachers)

def create_pdf(model: List[str], disp_teachers: List[dict], subjects: List[str], classrooms: List[str], hours: int, start_time: str, filename: str = "offered_subjects.pdf"):
    offered_subjects: List[dict] = decode_model(model, disp_teachers, subjects, classrooms, hours, start_time)

    doc = fitz.Document()
    n: int = 0
    while n < len(offered_subjects):
        # Create a new page in horizontal format
        page = doc.new_page(width=842, height=595)
        rect = page.rect + (36, 36, -36, -36)

        # Show 15 subjects per page
        m: int = n + 15 if n + 15 < len(offered_subjects) else len(offered_subjects)
        sub_offered: List[dict] = offered_subjects[n:m]

        text = html_code(offered_subjects)

        # we must specify an Archive because of the image
        page.insert_htmlbox(rect, text, archive=fitz.Archive("."))
        n += 15

    doc.ez_save(filename)