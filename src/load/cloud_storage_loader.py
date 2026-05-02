import os
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

def get_gcs_client():
    """
    Crea y devuelve un cliente de Google Cloud Storage.
    """
    client = storage.Client.from_service_account_json(
        GCP_CREDENTIALS_PATH,
        project=GCP_PROJECT_ID
    )
    return client


def upload_file_to_gcs(local_filepath: str, destination_blob_name: str) -> str:
    """
    Sube un fichero local a GCS.
    Devuelve la URI del fichero en GCS.
    """
    client = get_gcs_client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(local_filepath)

    gcs_uri = f"gs://{GCS_BUCKET_NAME}/{destination_blob_name}"
    print(f"✅ Fichero subido a GCS: {gcs_uri}")
    return gcs_uri


if __name__ == "__main__":
    # Prueba rápida — sube el último fichero generado en data_temp
    import glob

    files = glob.glob("data_temp/*.json")
    if not files:
        print("❌ No hay ficheros en data_temp/. Ejecuta primero weather_extractor.py")
    else:
        # Coge el fichero más reciente
        latest_file = max(files, key=os.path.getctime)
        filename = os.path.basename(latest_file)

        # En GCS lo guardamos dentro de una carpeta weather/raw/
        destination = f"weather/raw/{filename}"

        print(f"📤 Subiendo {filename} a GCS...")
        upload_file_to_gcs(latest_file, destination)