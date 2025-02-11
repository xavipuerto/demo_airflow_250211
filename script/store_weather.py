import sys
import json
from sqlalchemy import create_engine, Table, Column, Integer, TIMESTAMP, Text, JSON, MetaData
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configuración de la conexión con SQLAlchemy
DB_URI = "postgresql+psycopg2://postgres:password@emasesa-timescaledb-1:5432/postgres"
engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)

# Definir la estructura de las tablas
metadata = MetaData()

weather_madrid = Table(
    "weather_madrid", metadata,
    Column("id", Integer, primary_key=True),
    Column("ts", TIMESTAMP, nullable=False, default=datetime.utcnow),
    Column("api_url", Text, nullable=False),
    Column("data", JSON, nullable=False),
    Column("received_at", TIMESTAMP, nullable=False, default=datetime.utcnow),
    schema="public_api"
)

weather_paris = Table(
    "weather_paris", metadata,
    Column("id", Integer, primary_key=True),
    Column("ts", TIMESTAMP, nullable=False, default=datetime.utcnow),
    Column("api_url", Text, nullable=False),
    Column("data", JSON, nullable=False),
    Column("received_at", TIMESTAMP, nullable=False, default=datetime.utcnow),
    schema="public_api"
)

def store_weather_data():
    try:
        if len(sys.argv) < 2:
            raise ValueError("No se recibieron archivos JSON como argumento.")

        file_path = sys.argv[1]
        with open(file_path, "r") as f:
            weather_data = json.load(f)

        location = weather_data['location']
        api_url = weather_data['api_url']
        data = weather_data['data']

        session = Session()
        if location == "madrid":
            insert_stmt = weather_madrid.insert().values(
                api_url=api_url, data=data, received_at=datetime.utcnow()
            )
        elif location == "paris":
            insert_stmt = weather_paris.insert().values(
                api_url=api_url, data=data, received_at=datetime.utcnow()
            )
        else:
            print(f"Ubicación desconocida: {location}, ignorando entrada.", file=sys.stderr)
            sys.exit(1)

        session.execute(insert_stmt)
        session.commit()
        session.close()
        print(f"Datos almacenados correctamente en TimescaleDB para {location}.")
    
    except Exception as e:
        print(f"Error almacenando datos: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    store_weather_data()
