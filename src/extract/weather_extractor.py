import requests
import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Cargamos las variables del fichero .env
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("OPENWEATHER_CITY")


def get_weather_data(city: str) -> dict:
    """
    Llama a la API de OpenWeather y devuelve los datos en crudo.
    """
    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",  # Celsius
        "lang": "es"
    }

    response = requests.get(url, params=params)

    # Si hay error, lanza una excepción con el detalle
    response.raise_for_status()

    data = response.json()

    # Añadimos timestamp de cuándo hemos extraído el dato
    data["extracted_at"] = datetime.now(timezone.utc).isoformat()

    return data


def save_locally(data: dict, city: str) -> str:
    """
    Guarda los datos en local como JSON temporal.
    Devuelve la ruta del fichero creado.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"weather_{city.lower()}_{timestamp}.json"
    filepath = os.path.join("data_temp", filename)

    # Creamos la carpeta temporal si no existe
    os.makedirs("data_temp", exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f" Datos guardados localmente: {filepath}")
    return filepath


if __name__ == "__main__":
    print(f" Extrayendo datos del tiempo para: {CITY}")

    weather = get_weather_data(CITY)

    print(f"️ Temperatura: {weather['main']['temp']}°C")
    print(f" Humedad: {weather['main']['humidity']}%")
    print(f"️ Viento: {weather['wind']['speed']} m/s")

    filepath = save_locally(weather, CITY)