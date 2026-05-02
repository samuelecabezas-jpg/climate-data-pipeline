import os
from dotenv import load_dotenv
from extract.weather_extractor import get_weather_data, save_locally
from load.cloud_storage_loader import upload_file_to_gcs
import load.bq_loader as bql

load_dotenv()

CITY = os.getenv("OPENWEATHER_CITY")


def run_pipeline():
    print("Iniciando pipeline...")

    # Paso 1 — Extraer datos de la API
    print(f"\n Extrayendo datos para: {CITY}")
    weather_data = get_weather_data(CITY)
    print(f" Temperatura: {weather_data['main']['temp']}°C")
    print(f" Humedad: {weather_data['main']['humidity']}%")
    print(f" Viento: {weather_data['wind']['speed']} m/s")

    # Paso 2 — Guardar en local temporalmente
    local_filepath = save_locally(weather_data, CITY)

    # Paso 3 — Subir a GCS
    filename = os.path.basename(local_filepath)
    destination = f"weather/raw/{filename}"
    print(f"\n Subiendo a Cloud Storage...")
    gcs_uri = upload_file_to_gcs(local_filepath, destination)

    print(f"\n Pipeline completado!")
    print(f" Fichero disponible en: {gcs_uri}")

    # Paso 4 - Almacenar en BigQuery

    import glob
    files=glob.glob('data_temp/*.json')
    if not files:
        print(f"\n No hay ficheros en data_temp")
    else:
        latest_file=max(files,key=os.path.getctime)
        print(f"\n Subiendo {latest_file} a BigQuery")
        bql.load_to_bigquery(latest_file)


if __name__ == "__main__":
    run_pipeline()