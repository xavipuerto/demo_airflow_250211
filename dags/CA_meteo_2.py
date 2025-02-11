from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Configuración del DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 2, 11),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "weather_data_pipeline_emasesa",
    default_args=default_args,
    schedule_interval="@hourly",
    catchup=False
)

# Tareas para obtener datos de Madrid y París
fetch_madrid = BashOperator(
    task_id="fetch_weather_madrid",
    bash_command="python /opt/emasesa/script/fetch_weather.py madrid > /tmp/weather_madrid.json",
    dag=dag
)

fetch_paris = BashOperator(
    task_id="fetch_weather_paris",
    bash_command="python /opt/emasesa/script/fetch_weather.py paris > /tmp/weather_paris.json",
    dag=dag
)

# Tareas para almacenar datos en las tablas individuales
store_madrid = BashOperator(
    task_id="store_weather_madrid",
    bash_command="python /opt/emasesa/script/store_weather.py /tmp/weather_madrid.json",
    dag=dag
)

store_paris = BashOperator(
    task_id="store_weather_paris",
    bash_command="python /opt/emasesa/script/store_weather.py /tmp/weather_paris.json",
    dag=dag
)

# Tarea para consolidar los datos en una tabla final
consolidate_data = BashOperator(
    task_id="consolidate_weather_data",
    bash_command="python /opt/emasesa/script/consolidate_weather.py",
    dag=dag
)

# Definir la secuencia de ejecución
fetch_madrid >> store_madrid
fetch_paris >> store_paris
[store_madrid, store_paris] >> consolidate_data
