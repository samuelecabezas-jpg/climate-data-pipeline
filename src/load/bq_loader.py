import os
import json
from datetime import datetime, timezone
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")
BQ_DATASET = os.getenv("BQ_DATASET")
BQ_TABLE = os.getenv("BQ_TABLE")


def get_bq_client():
    """
    Crea y devuelve un cliente de BigQuery.
    """
    client = bigquery.Client.from_service_account_json(
        GCP_CREDENTIALS_PATH,
        project=GCP_PROJECT_ID
    )
    return client


def flatten_weather_data(raw: dict) -> dict:
    """
    La API devuelve JSON anidado, lo aplanamos a una fila simple
    para poder meterlo en una tabla de BigQuery.
    """
    return {
        "city":             raw.get("name"),
        "country":          raw.get("sys", {}).get("country"),
        "temperature":      raw.get("main", {}).get("temp"),
        "feels_like":       raw.get("main", {}).get("feels_like"),
        "temp_min":         raw.get("main", {}).get("temp_min"),
        "temp_max":         raw.get("main", {}).get("temp_max"),
        "humidity":         raw.get("main", {}).get("humidity"),
        "pressure":         raw.get("main", {}).get("pressure"),
        "wind_speed":       raw.get("wind", {}).get("speed"),
        "wind_deg":         raw.get("wind", {}).get("deg"),
        "weather_main":     raw.get("weather", [{}])[0].get("main"),
        "weather_desc":     raw.get("weather", [{}])[0].get("description"),
        "cloudiness":       raw.get("clouds", {}).get("all"),
        "visibility":       raw.get("visibility"),
        "extracted_at":     raw.get("extracted_at"),
        "loaded_at":        datetime.now(timezone.utc).isoformat(),
    }


def create_table_if_not_exists(client: bigquery.Client):
    """
    Crea la tabla en BigQuery si no existe todavía,
    con el schema definido.
    """
    table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"

    schema = [
        bigquery.SchemaField("city",          "STRING"),
        bigquery.SchemaField("country",       "STRING"),
        bigquery.SchemaField("temperature",   "FLOAT"),
        bigquery.SchemaField("feels_like",    "FLOAT"),
        bigquery.SchemaField("temp_min",      "FLOAT"),
        bigquery.SchemaField("temp_max",      "FLOAT"),
        bigquery.SchemaField("humidity",      "INTEGER"),
        bigquery.SchemaField("pressure",      "INTEGER"),
        bigquery.SchemaField("wind_speed",    "FLOAT"),
        bigquery.SchemaField("wind_deg",      "INTEGER"),
        bigquery.SchemaField("weather_main",  "STRING"),
        bigquery.SchemaField("weather_desc",  "STRING"),
        bigquery.SchemaField("cloudiness",    "INTEGER"),
        bigquery.SchemaField("visibility",    "INTEGER"),
        bigquery.SchemaField("extracted_at",  "STRING"),
        bigquery.SchemaField("loaded_at",     "STRING"),
    ]

    table = bigquery.Table(table_id, schema=schema)

    client.create_table(table, exists_ok=True)
    print(f"✅ Tabla lista: {table_id}")


def load_to_bigquery(local_filepath: str):
    """
    Lee un fichero JSON local, lo aplana y lo inserta en BigQuery.
    """
    client = get_bq_client()
    table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"

    # Nos aseguramos de que la tabla existe
    create_table_if_not_exists(client)

    # Leemos el JSON
    with open(local_filepath, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Aplanamos el JSON anidado
    row = flatten_weather_data(raw_data)

    # Insertamos la fila en BigQuery
    errors = client.insert_rows_json(table_id, [row])

    if errors:
        print(f" Errores al insertar en BigQuery: {errors}")
    else:
        print(f" Fila insertada correctamente en {table_id}")
        print(f" Ciudad:      {row['city']}, {row['country']}")
        print(f" Temperatura: {row['temperature']}°C")
        print(f" Tiempo:      {row['weather_desc']}")


if __name__ == "__main__":
    import glob

    files = glob.glob("data_temp/*.json")
    if not files:
        print("❌ No hay ficheros en data_temp/. Ejecuta primero el pipeline.")
    else:
        latest_file = max(files, key=os.path.getctime)
        print(f"📤 Cargando {latest_file} en BigQuery...")
        load_to_bigquery(latest_file)