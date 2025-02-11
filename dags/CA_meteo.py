from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import psycopg2
import json

# Configuración de la conexión a TimescaleDB
DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "password",
    "host": "emasesa-timescaledb-1",
    "port": "5432"
}

# API Pública (ejemplo: Open-Meteo para datos meteorológicos)
BASE_API_URL = "https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"

LOCATIONS = {
    "madrid": {"latitude": 40.4165, "longitude": -3.70256},
    "paris": {"latitude": 48.8566, "longitude": 2.3522}
}

def fetch_and_store_data(location_name, latitude, longitude):
    api_url = BASE_API_URL.format(latitude=latitude, longitude=longitude)
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        save_to_timescaledb(data, location_name, api_url)
    else:
        raise Exception(f"Error en la API para {location_name}: {response.status_code}")

def save_to_timescaledb(data, location_name, api_url):
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    query = """
        INSERT INTO public_api.api_data (location, api_url, data)
        VALUES (%s, %s, %s)
    """
    cursor.execute(query, (location_name, api_url, json.dumps({"location": location_name, "data": data})))
    conn.commit()
    cursor.close()
    conn.close()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 2, 11),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "get_data_meteo",
    default_args=default_args,
    schedule_interval="@hourly",
    catchup=False
)

task_fetch_madrid = PythonOperator(
    task_id="fetch_and_store_madrid",
    python_callable=fetch_and_store_data,
    op_args=["madrid", LOCATIONS["madrid"]["latitude"], LOCATIONS["madrid"]["longitude"]],
    dag=dag
)

task_fetch_paris = PythonOperator(
    task_id="fetch_and_store_paris",
    python_callable=fetch_and_store_data,
    op_args=["paris", LOCATIONS["paris"]["latitude"], LOCATIONS["paris"]["longitude"]],
    dag=dag
)

task_fetch_madrid >> task_fetch_paris
