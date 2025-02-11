import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuración de la conexión con SQLAlchemy
DB_URI = "postgresql+psycopg2://postgres:password@emasesa-timescaledb-1:5432/postgres"
engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)

def consolidate_weather_data():
    try:
        session = Session()
        
        # Crear tabla consolidada si no existe
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS public_api.weather_consolidated (
                id SERIAL PRIMARY KEY,
                ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                location TEXT NOT NULL,
                api_url TEXT NOT NULL,
                data JSONB NOT NULL,
                received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """))
        session.commit()
        
        # Insertar datos de Madrid y París en la tabla consolidada
        session.execute(text("""
            INSERT INTO public_api.weather_consolidated (location, api_url, data, received_at)
            SELECT 'madrid', api_url, data, received_at FROM public_api.weather_madrid
            UNION ALL
            SELECT 'paris', api_url, data, received_at FROM public_api.weather_paris;
        """))
        session.commit()
        session.close()
        print("Consolidación de datos completada correctamente.")
    
    except Exception as e:
        print(f"Error consolidando datos: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    consolidate_weather_data()
