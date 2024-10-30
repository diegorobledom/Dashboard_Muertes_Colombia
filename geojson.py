import os
import requests
import json

# Definir la ruta donde se guardará el archivo GeoJSON
geojson_path = 'colombia_departments.geojson'
url = 'https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json'

def download_geojson(url, save_path):
    """Descarga el archivo GeoJSON desde una URL y lo guarda en la ruta especificada."""
    response = requests.get(url)
    response.raise_for_status()  # Lanza una excepción si hay un error en la descarga
    with open(save_path, 'w') as f:
        json.dump(response.json(), f)
    print(f"Archivo descargado y guardado como {save_path}")

def load_geojson(local_path):
    """Carga el archivo GeoJSON desde una ruta local."""
    with open(local_path, 'r') as f:
        return json.load(f)

# Verificar si el archivo existe localmente
if not os.path.exists(geojson_path):
    print("El archivo no existe localmente. Descargando...")
    download_geojson(url, geojson_path)
#else:
#    print(f"El archivo {geojson_path} ya existe localmente. No se requiere descarga.")

# Cargar el archivo GeoJSON desde la ruta local
colombia_geojson = load_geojson(geojson_path)
