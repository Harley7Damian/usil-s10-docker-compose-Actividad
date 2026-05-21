import os
from datetime import datetime, time, timedelta
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

DAYS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

COURSE_IMAGES = {
    "Cloud Computing": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=900&q=80",
    "Base de Datos": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=900&q=80",
    "Gestion de Proyectos": "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=900&q=80",
    "Arquitectura de Software": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=900&q=80",
}

COLOR_PALETTE = ["#2f80ed", "#00a676", "#f2994a", "#9b51e0", "#eb5757", "#00897b"]


def oid(value: Any) -> ObjectId:
    return ObjectId(str(value))


def h(value: Any) -> str:
    return escape(str(value or ""))


@st.cache_resource
def get_database():
    try:
        secret_uri = st.secrets.get("MONGO_URI")
        secret_db = st.secrets.get("MONGO_DB", None)
    except Exception:
        secret_uri = None
        secret_db = None

    mongo_uri = secret_uri or os.getenv("MONGO_URI", "mongodb://mongo:27017/")
    db_name = secret_db or os.getenv("MONGO_DB", "campus_notion")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2500)
    client.admin.command("ping")
    return client[db_name]


def get_db_or_stop():
    try:
        return get_database()
    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        st.error(
            "No se pudo conectar a MongoDB. Revisa `MONGO_URI` en Streamlit Secrets "
            "o levanta el proyecto con `docker compose up`."
        )
        st.caption(str(exc))
        st.stop()


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
            --ink: #17202a;
            --muted: #5f6c7b;
            --paper: #fbfaf7;
            --line: #e7e0d3;
            --accent: #2f80ed;
            --mint: #00a676;
            --sun: #f2994a;
        }

        .stApp {
            background:
                linear-gradient(120deg, rgba(47,128,237,.10), rgba(0,166,118,.07)),
                var(--paper);
            color: var(--ink);
        }

        [data-testid="stSidebar"] {
            background: #f3efe7;
            border-right: 1px solid var(--line);
        }

        h1, h2, h3 {
            letter-spacing: 0;
        }

        .hero {
            min-height: 250px;
            border-bottom: 1px solid var(--line);
            margin: -3.8rem -4rem 2rem -4rem;
            padding: 4rem 4rem 2rem 4rem;
            background:
                linear-gradient(90deg, rgba(20,31,43,.78), rgba(20,31,43,.18)),
                url("https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1600&q=80");
            background-size: cover;
            background-position: center;
            color: white;
        }

        .hero h1 {
            font-size: clamp(2.2rem, 4vw, 4rem);
            line-height: 1.02;
            margin: 0;
        }

        .hero p {
            max-width: 680px;
            font-size: 1.06rem;
            color: rgba(255,255,255,.88);
        }

        .metric-strip {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: .8rem;
            margin-bottom: 1.2rem;
        }

        .metric-card, .course-card, .notice, .task-card, .resource-card {
            background: rgba(255,255,255,.78);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: 0 12px 30px rgba(23,32,42,.06);
        }

        .metric-card {
            padding: 1rem;
        }

        .metric-card span {
            color: var(--muted);
            font-size: .82rem;
        }

        .metric-card strong {
            display: block;
            font-size: 1.7rem;
            margin-top: .15rem;
        }

        .notice {
            padding: 1rem;
            border-left: 5px solid var(--accent);
        }

        .notice h3 {
            margin: 0 0 .25rem 0;
        }

        .course-card {
            overflow: hidden;
            min-height: 260px;
            margin-bottom: 1rem;
        }

        .course-cover {
            height: 112px;
            background-size: cover;
            background-position: center;
        }

        .course-body {
            padding: 1rem;
        }

        .course-pill {
            display: inline-block;
            padding: .2rem .55rem;
            border-radius: 999px;
            color: white;
            font-size: .78rem;
            margin-bottom: .55rem;
        }

        .schedule-grid {
            display: grid;
            grid-template-columns: repeat(7, minmax(140px, 1fr));
            gap: .75rem;
            overflow-x: auto;
            padding-bottom: .4rem;
        }

        .day-column {
            min-height: 300px;
            background: rgba(255,255,255,.62);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: .65rem;
        }

        .day-title {
            font-weight: 700;
            margin-bottom: .5rem;
        }

        .class-chip {
            border-radius: 8px;
            color: white;
            padding: .55rem;
            margin-bottom: .55rem;
            font-size: .85rem;
        }

        .class-chip strong {
            display: block;
            font-size: .92rem;
        }

        .task-card, .resource-card {
            padding: .85rem;
            margin-bottom: .7rem;
        }

        .task-card small, .resource-card small {
            color: var(--muted);
        }

        @media (max-width: 900px) {
            .hero {
                margin-left: -1rem;
                margin-right: -1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .metric-strip {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def seed_data(db):
    if db.courses.count_documents({}) > 0:
        return

    now = datetime.now()
    courses = [
        {
            "name": "Cloud Computing",
            "teacher": "Mg. Rivera",
            "room": "Lab 402",
            "color": "#2f80ed",
            "image": COURSE_IMAGES["Cloud Computing"],
            "credits": 4,
            "notes": "Docker, Streamlit, despliegues y servicios cloud.",
            "created_at": now,
        },
        {
            "name": "Base de Datos",
            "teacher": "Dra. Salazar",
            "room": "Aula 305",
            "color": "#00a676",
            "image": COURSE_IMAGES["Base de Datos"],
            "credits": 3,
            "notes": "Modelado, consultas, indices y MongoDB.",
            "created_at": now,
        },
        {
            "name": "Gestion de Proyectos",
            "teacher": "Ing. Vega",
            "room": "Aula 210",
            "color": "#f2994a",
            "image": COURSE_IMAGES["Gestion de Proyectos"],
            "credits": 3,
            "notes": "Planificacion, entregables y seguimiento semanal.",
            "created_at": now,
        },
    ]
    result = db.courses.insert_many(courses)
    by_name = dict(zip([course["name"] for course in courses], result.inserted_ids))

    db.classes.insert_many(
        [
            {
                "course_id": by_name["Cloud Computing"],
                "day": "Lunes",
                "start": "18:00",
                "end": "20:00",
                "topic": "Laboratorio con Docker Compose",
                "mode": "Presencial",
            },
            {
                "course_id": by_name["Cloud Computing"],
                "day": "Miercoles",
                "start": "19:00",
                "end": "21:00",
                "topic": "Despliegue de apps",
                "mode": "Virtual",
            },
            {
                "course_id": by_name["Base de Datos"],
                "day": "Martes",
                "start": "16:00",
                "end": "18:00",
                "topic": "Colecciones e indices",
                "mode": "Presencial",
            },
            {
                "course_id": by_name["Gestion de Proyectos"],
                "day": "Jueves",
                "start": "20:00",
                "end": "22:00",
                "topic": "Sprint review",
                "mode": "Presencial",
            },
        ]
    )

    db.tasks.insert_many(
        [
            {
                "course_id": by_name["Cloud Computing"],
                "title": "Subir app a GitHub",
                "due_date": (now + timedelta(days=2)).date().isoformat(),
                "status": "Pendiente",
                "priority": "Alta",
            },
            {
                "course_id": by_name["Base de Datos"],
                "title": "Disenar coleccion de horarios",
                "due_date": (now + timedelta(days=5)).date().isoformat(),
                "status": "En progreso",
                "priority": "Media",
            },
        ]
    )


def fetch_courses(db):
    return list(db.courses.find().sort("name", 1))


def course_map(courses):
    return {str(course["_id"]): course for course in courses}


def next_occurrence(day: str, start: str) -> datetime:
    now = datetime.now()
    target_weekday = DAYS.index(day)
    hour, minute = [int(part) for part in start.split(":")]
    candidate = datetime.combine(now.date(), time(hour, minute))
    days_ahead = (target_weekday - now.weekday()) % 7
    candidate += timedelta(days=days_ahead)
    if candidate < now:
        candidate += timedelta(days=7)
    return candidate


def get_upcoming_classes(db, courses_by_id):
    rows = []
    for item in db.classes.find():
        course = courses_by_id.get(str(item["course_id"]))
        if not course:
            continue
        starts_at = next_occurrence(item["day"], item["start"])
        rows.append({**item, "course": course, "starts_at": starts_at})
    return sorted(rows, key=lambda row: row["starts_at"])


def render_hero():
    st.markdown(
        """
        <section class="hero">
            <h1>Campus OS</h1>
            <p>Un tablero academico para organizar cursos, horarios, tareas y recursos con una vibra limpia tipo Notion.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(courses, classes, tasks):
    pending = [task for task in tasks if task.get("status") != "Completada"]
    week_hours = 0
    for item in classes:
        start = datetime.strptime(item["start"], "%H:%M")
        end = datetime.strptime(item["end"], "%H:%M")
        week_hours += max((end - start).seconds / 3600, 0)

    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-card"><span>Cursos activos</span><strong>{len(courses)}</strong></div>
            <div class="metric-card"><span>Clases semanales</span><strong>{len(classes)}</strong></div>
            <div class="metric-card"><span>Tareas abiertas</span><strong>{len(pending)}</strong></div>
            <div class="metric-card"><span>Horas por semana</span><strong>{week_hours:.0f}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_next_class(upcoming):
    if not upcoming:
        st.info("Agrega clases a tu horario para activar los recordatorios.")
        return

    item = upcoming[0]
    delta = item["starts_at"] - datetime.now()
    hours = int(delta.total_seconds() // 3600)
    minutes = int((delta.total_seconds() % 3600) // 60)
    course = item["course"]

    if delta <= timedelta(hours=2):
        st.toast(f"Proxima clase: {course['name']} a las {item['start']}")

    st.markdown(
        f"""
        <div class="notice">
            <h3>Proxima clase: {h(course['name'])}</h3>
            <div>{h(item['day'])} {h(item['start'])} - {h(item['end'])} - {h(course.get('room', 'Sin aula'))} - {h(item.get('mode', 'Clase'))}</div>
            <strong>Faltan {hours}h {minutes}m</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_course_cards(courses, upcoming_by_course):
    cols = st.columns(3)
    for index, course in enumerate(courses):
        next_class = upcoming_by_course.get(str(course["_id"]))
        detail = "Sin clase programada"
        if next_class:
            detail = f"{next_class['day']} {next_class['start']} - {next_class['topic']}"

        with cols[index % 3]:
            st.markdown(
                f"""
                <article class="course-card">
                    <div class="course-cover" style="background-image:url('{h(course.get('image', COURSE_IMAGES['Cloud Computing']))}')"></div>
                    <div class="course-body">
                        <span class="course-pill" style="background:{h(course.get('color', '#2f80ed'))}">{h(course.get('credits', 0))} creditos</span>
                        <h3>{h(course['name'])}</h3>
                        <p>{h(course.get('notes', ''))}</p>
                        <small>{h(course.get('teacher', 'Docente por definir'))} - {h(course.get('room', 'Sin aula'))}</small><br>
                        <small>{h(detail)}</small>
                    </div>
                </article>
                """,
                unsafe_allow_html=True,
            )


def render_schedule(classes, courses_by_id):
    html = ['<div class="schedule-grid">']
    for day in DAYS:
        chips = []
        day_classes = sorted(
            [item for item in classes if item["day"] == day],
            key=lambda item: item["start"],
        )
        for item in day_classes:
            course = courses_by_id.get(str(item["course_id"]), {})
            chips.append(
                f"""
                <div class="class-chip" style="background:{h(course.get('color', '#2f80ed'))}">
                    <strong>{h(item['start'])} - {h(course.get('name', 'Curso'))}</strong>
                    {h(item.get('topic', 'Clase'))}<br>
                    <small>{h(item.get('mode', ''))} - {h(course.get('room', ''))}</small>
                </div>
                """
            )
        content = "".join(chips) or "<small>Sin clases</small>"
        html.append(
            f"""
            <div class="day-column">
                <div class="day-title">{h(day)}</div>
                {content}
            </div>
            """
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def sidebar_forms(db, courses):
    st.sidebar.title("Panel de control")
    options = {course["name"]: str(course["_id"]) for course in courses}

    with st.sidebar.expander("Nuevo curso", expanded=True):
        with st.form("course_form", clear_on_submit=True):
            name = st.text_input("Nombre del curso")
            teacher = st.text_input("Docente")
            room = st.text_input("Aula o enlace")
            credits = st.number_input("Creditos", min_value=1, max_value=8, value=3)
            color = st.selectbox("Color", COLOR_PALETTE)
            notes = st.text_area("Notas breves")
            image = st.text_input("URL de imagen", value=COURSE_IMAGES["Cloud Computing"])
            if st.form_submit_button("Guardar curso", use_container_width=True):
                if not name.strip():
                    st.warning("Escribe el nombre del curso.")
                else:
                    db.courses.insert_one(
                        {
                            "name": name.strip(),
                            "teacher": teacher.strip(),
                            "room": room.strip(),
                            "credits": credits,
                            "color": color,
                            "notes": notes.strip(),
                            "image": image.strip(),
                            "created_at": datetime.now(),
                        }
                    )
                    st.success("Curso guardado.")
                    st.rerun()

    with st.sidebar.expander("Nueva clase"):
        if not options:
            st.caption("Crea un curso primero.")
        else:
            with st.form("class_form", clear_on_submit=True):
                course_name = st.selectbox("Curso", list(options.keys()))
                day = st.selectbox("Dia", DAYS)
                col1, col2 = st.columns(2)
                start = col1.time_input("Inicio", value=time(18, 0))
                end = col2.time_input("Fin", value=time(20, 0))
                topic = st.text_input("Tema")
                mode = st.selectbox("Modalidad", ["Presencial", "Virtual", "Hibrida"])
                if st.form_submit_button("Agregar clase", use_container_width=True):
                    db.classes.insert_one(
                        {
                            "course_id": oid(options[course_name]),
                            "day": day,
                            "start": start.strftime("%H:%M"),
                            "end": end.strftime("%H:%M"),
                            "topic": topic.strip() or "Clase",
                            "mode": mode,
                        }
                    )
                    st.success("Clase agregada.")
                    st.rerun()

    with st.sidebar.expander("Nueva tarea"):
        if not options:
            st.caption("Crea un curso primero.")
        else:
            with st.form("task_form", clear_on_submit=True):
                course_name = st.selectbox("Curso", list(options.keys()), key="task_course")
                title = st.text_input("Tarea")
                due_date = st.date_input("Fecha limite", value=datetime.now().date())
                priority = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
                if st.form_submit_button("Guardar tarea", use_container_width=True):
                    if title.strip():
                        db.tasks.insert_one(
                            {
                                "course_id": oid(options[course_name]),
                                "title": title.strip(),
                                "due_date": due_date.isoformat(),
                                "status": "Pendiente",
                                "priority": priority,
                            }
                        )
                        st.success("Tarea guardada.")
                        st.rerun()

    with st.sidebar.expander("Administrar datos"):
        if not options:
            st.caption("No hay cursos para administrar.")
        else:
            delete_course = st.selectbox("Eliminar curso", list(options.keys()))
            if st.button("Eliminar curso y datos", use_container_width=True):
                course_id = oid(options[delete_course])
                db.classes.delete_many({"course_id": course_id})
                db.tasks.delete_many({"course_id": course_id})
                db.courses.delete_one({"_id": course_id})
                st.warning("Curso eliminado con sus clases y tareas.")
                st.rerun()

        class_rows = list(db.classes.find())
        class_options = {}
        for item in class_rows:
            course = next(
                (course for course in courses if course["_id"] == item["course_id"]),
                {"name": "Curso"},
            )
            label = f"{course['name']} - {item['day']} {item['start']}"
            class_options[label] = str(item["_id"])

        if class_options:
            delete_class = st.selectbox("Eliminar clase", list(class_options.keys()))
            if st.button("Eliminar clase", use_container_width=True):
                db.classes.delete_one({"_id": oid(class_options[delete_class])})
                st.warning("Clase eliminada.")
                st.rerun()


def render_tasks(db, tasks, courses_by_id):
    for task in sorted(tasks, key=lambda item: item.get("due_date", "")):
        course = courses_by_id.get(str(task["course_id"]), {})
        cols = st.columns([0.08, 0.62, 0.2, 0.1])
        done = task.get("status") == "Completada"
        checked = cols[0].checkbox("", value=done, key=f"task-{task['_id']}")
        if checked != done:
            db.tasks.update_one(
                {"_id": task["_id"]},
                {"$set": {"status": "Completada" if checked else "Pendiente"}},
            )
            st.rerun()
        cols[1].markdown(
            f"""
            <div class="task-card">
                <strong>{h(task['title'])}</strong><br>
                <small>{h(course.get('name', 'Curso'))} - Prioridad {h(task.get('priority', 'Media'))}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cols[2].write(task.get("due_date", ""))
        if cols[3].button("Borrar", key=f"delete-task-{task['_id']}"):
            db.tasks.delete_one({"_id": task["_id"]})
            st.rerun()


def render_resources():
    st.subheader("Recursos")
    uploaded_file = st.file_uploader("Sube apuntes, silabos o entregables")
    if uploaded_file:
        file_path = UPLOAD_DIR / uploaded_file.name
        with open(file_path, "wb") as file:
            file.write(uploaded_file.getbuffer())
        st.success(f"Archivo guardado: {file_path}")

    files = sorted(UPLOAD_DIR.iterdir())
    if not files:
        st.caption("Todavia no hay archivos subidos.")
        return

    for file in files:
        st.markdown(
            f"""
            <div class="resource-card">
                <strong>{h(file.name)}</strong><br>
                <small>{file.stat().st_size / 1024:.1f} KB</small>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_data_tools(db, courses, classes, tasks, courses_by_id):
    st.subheader("Datos guardados en MongoDB")
    tab_courses, tab_classes, tab_tasks = st.tabs(["Cursos", "Clases", "Tareas"])

    with tab_courses:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "id": str(course["_id"]),
                        "curso": course["name"],
                        "docente": course.get("teacher", ""),
                        "aula": course.get("room", ""),
                        "creditos": course.get("credits", 0),
                    }
                    for course in courses
                ]
            ),
            use_container_width=True,
        )

    with tab_classes:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "curso": courses_by_id.get(str(item["course_id"]), {}).get("name", ""),
                        "dia": item["day"],
                        "inicio": item["start"],
                        "fin": item["end"],
                        "tema": item.get("topic", ""),
                        "modalidad": item.get("mode", ""),
                    }
                    for item in classes
                ]
            ),
            use_container_width=True,
        )

    with tab_tasks:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "curso": courses_by_id.get(str(item["course_id"]), {}).get("name", ""),
                        "tarea": item["title"],
                        "fecha": item.get("due_date", ""),
                        "estado": item.get("status", ""),
                        "prioridad": item.get("priority", ""),
                    }
                    for item in tasks
                ]
            ),
            use_container_width=True,
        )

    if st.button("Cargar datos demo de nuevo", use_container_width=True):
        db.courses.delete_many({})
        db.classes.delete_many({})
        db.tasks.delete_many({})
        seed_data(db)
        st.rerun()


def main():
    st.set_page_config(page_title="Campus OS", layout="wide")
    inject_styles()

    db = get_db_or_stop()
    seed_data(db)

    courses = fetch_courses(db)
    courses_by_id = course_map(courses)
    classes = list(db.classes.find())
    tasks = list(db.tasks.find())
    upcoming = get_upcoming_classes(db, courses_by_id)
    upcoming_by_course = {}
    for item in upcoming:
        upcoming_by_course.setdefault(str(item["course_id"]), item)

    sidebar_forms(db, courses)
    render_hero()
    render_metrics(courses, classes, tasks)
    render_next_class(upcoming)

    overview_tab, schedule_tab, tasks_tab, resources_tab, data_tab = st.tabs(
        ["Dashboard", "Horario", "Tareas", "Recursos", "MongoDB"]
    )

    with overview_tab:
        st.subheader("Cursos")
        render_course_cards(courses, upcoming_by_course)

    with schedule_tab:
        st.subheader("Horario semanal")
        render_schedule(classes, courses_by_id)

    with tasks_tab:
        st.subheader("Pendientes")
        render_tasks(db, tasks, courses_by_id)

    with resources_tab:
        render_resources()

    with data_tab:
        render_data_tools(db, courses, classes, tasks, courses_by_id)


if __name__ == "__main__":
    main()
