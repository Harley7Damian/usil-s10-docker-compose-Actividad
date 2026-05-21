# Campus OS - Streamlit + MongoDB

Aplicacion academica tipo Notion para organizar cursos, horarios, tareas y recursos de la universidad. Incluye recordatorios visuales de la proxima clase y persistencia en MongoDB.

## Funcionalidades

- Dashboard visual con cursos activos, clases semanales, tareas pendientes y horas por semana.
- CRUD de cursos, clases y tareas usando MongoDB.
- Horario semanal por dias.
- Aviso tipo popup con `st.toast` cuando una clase esta cerca.
- Subida local de recursos academicos en `streamlit/uploads`.
- Datos demo automaticos para probar la app desde el primer inicio.

## Ejecutar con Docker Compose

```bash
docker compose up
```

Abre la app en:

```text
http://localhost:8501
```

El servicio de MongoDB queda disponible en `localhost:27017` y los datos se guardan en el volumen `mongo_data`.

## Ejecutar solo Streamlit

Instala dependencias:

```bash
pip install -r streamlit/requirements.txt
```

Define la URI de MongoDB:

```bash
set MONGO_URI=mongodb://localhost:27017/
set MONGO_DB=campus_notion
```

Ejecuta:

```bash
cd streamlit
streamlit run app.py
```

## Despliegue en Streamlit Community Cloud

1. Sube este proyecto a GitHub.
2. Crea una base MongoDB en MongoDB Atlas.
3. En Streamlit Cloud, configura el archivo principal como:

```text
streamlit/app.py
```

4. En `Secrets`, agrega:

```toml
MONGO_URI = "mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority"
```

Opcionalmente configura la variable de entorno:

```text
MONGO_DB=campus_notion
```

## Estructura

```text
.
+-- docker-compose.yml
+-- README.md
+-- streamlit
    +-- app.py
    +-- requirements.txt
    +-- uploads
```
