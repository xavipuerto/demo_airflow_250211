Weather Data Pipeline - Airflow & TimescaleDB

Este proyecto implementa una ETL para obtener datos meteorológicos de una API pública y almacenarlos en una base de datos TimescaleDB usando Airflow. Se orquestan tres tareas principales:

Obtener datos meteorológicos para Madrid y París desde open-meteo.com.

Guardar los datos en tablas separadas (weather_madrid y weather_paris).

Consolidar los datos en la tabla weather_consolidated.

📌 Estructura del Proyecto

/opt/emasesa/
├── dags/                   # DAGs de Airflow
│   ├── CA_meteo.py         # DAG con PythonOperators para llamadas API
│   ├── CA_meteo_2.py       # DAG con BashOperators para ejecución de scripts
├── script/                 # Scripts Python
│   ├── fetch_weather.py    # Obtiene los datos de la API
│   ├── store_weather.py    # Inserta los datos en la BD
│   ├── consolidate_weather.py  # Consolida los datos
├── logs/                   # Logs de ejecución
│   ├── fetch_weather.log
│   ├── store_weather.log
│   ├── consolidate_weather.log
└── README.md               # Documentación del proyecto

⚙️ Configuración del Entorno

📂 Creación de directorios

Ejecutar los siguientes comandos para asegurarse de que los directorios existen:

sudo mkdir -p /opt/emasesa/{dags,script,logs}

📦 Instalación de dependencias

Asegúrate de que tienes Docker y docker-compose instalados.
Instala las librerías necesarias dentro del contenedor Airflow:

pip install apache-airflow sqlalchemy psycopg2 requests

🚀 Levantar los servicios

El entorno se levanta con Docker Compose. Usa:

cd /opt/emasesa/
docker-compose up -d

Esto iniciará los contenedores de Airflow, PostgreSQL y TimescaleDB.

Accede a la UI de Airflow en:

http://localhost:8080
Usuario: admin
Contraseña: admin

🔌 Conexión a la Base de Datos

Puedes conectarte a la base de datos TimescaleDB desde un contenedor con:

docker exec -it emasesa-timescaledb-1 psql -U postgres -d postgres

O desde un cliente externo:

Host: localhost
Puerto: 5433
Usuario: postgres
Contraseña: password
Base de datos: postgres

📊 Creación del Esquema y Tablas

Para inicializar el esquema de datos en TimescaleDB, ejecuta:

CREATE SCHEMA IF NOT EXISTS public_api;

CREATE TABLE public_api.weather_madrid (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    api_url TEXT NOT NULL,
    data JSONB NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SELECT create_hypertable('public_api.weather_madrid', 'ts');

CREATE TABLE public_api.weather_paris (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    api_url TEXT NOT NULL,
    data JSONB NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SELECT create_hypertable('public_api.weather_paris', 'ts');

CREATE TABLE public_api.weather_consolidated (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    location TEXT NOT NULL,
    api_url TEXT NOT NULL,
    data JSONB NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

🔄 Flujo de Ejecución

El DAG de Airflow CA_meteo.py y CA_meteo_2.py gestionan la ejecución:

CA_meteo.py (Usa PythonOperator para llamada a API y almacenamiento directo en BD)

# Se ejecutan en Airflow
fetch_and_store_madrid
fetch_and_store_paris

CA_meteo_2.py (Usa BashOperator con scripts Python)

1️⃣ Descarga datos de la API:

python /opt/emasesa/script/fetch_weather.py madrid > /tmp/weather_madrid.json
python /opt/emasesa/script/fetch_weather.py paris > /tmp/weather_paris.json

2️⃣ Almacena los datos en TimescaleDB:

python /opt/emasesa/script/store_weather.py /tmp/weather_madrid.json
python /opt/emasesa/script/store_weather.py /tmp/weather_paris.json

3️⃣ Consolida los datos en una tabla final:

python /opt/emasesa/script/consolidate_weather.py

📡 Consultas SQL

Ver los datos almacenados:

SELECT * FROM public_api.weather_madrid;
SELECT * FROM public_api.weather_paris;
SELECT * FROM public_api.weather_consolidated;

🛠️ Depuración y Logs

Si un proceso falla, revisa los logs en /opt/emasesa/logs/:

cat /opt/emasesa/logs/fetch_weather.log
cat /opt/emasesa/logs/store_weather.log
cat /opt/emasesa/logs/consolidate_weather.log

O en la interfaz de Airflow en la pestaña Logs.

📌 Notas Finales

Los DAGs están programados para ejecutarse cada hora.

Si quieres forzar la ejecución, usa:

airflow dags trigger get_data_meteo
airflow dags trigger weather_data_pipeline_emasesa

Si quieres parar y eliminar los contenedores:

docker-compose down --volumes

🚀 Ahora el pipeline está listo para usarse! 🎯
