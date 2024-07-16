from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.exceptions import InfluxDBError
import influxdb_client
import mysql.connector
from localStoragePy import localStoragePy

from datetime import datetime
import time,os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
localStorage = localStoragePy('my_app_namespace', 'json')
# Definir variables de conexión
DB_PORT = localStorage.getItem('influx_port')
DB_HOST = localStorage.getItem('influx_host')
DB_ORG = localStorage.getItem('influx_org')
DB_TOKEN = localStorage.getItem('influx_token')
DB_BUCKET = localStorage.getItem('influx_bucket')


# Función para obtener la conexión a la base de datos
def check_influxdb_connection():
    host=DB_HOST
    port=DB_PORT
    org=DB_ORG
    token=DB_TOKEN
    url=f'http://{str(host)}:{str(port)}'
    
    
    try:
        client = InfluxDBClient(url,
                        str(token),
                        org,)
        health = client.health()
        if health.status == "pass":
                print("Connection successful.")
                return True
        else:
                print(f"Connection failed: {health.message}")
                return False
    except InfluxDBError as e:
        print(f"An error occurred: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def guardar_en_influxdb(topico, id, sensor, mensaje):
    intentos = 0
    
#     # Configuración de InfluxDB (reemplaza con tus datos)
#     url = "http://localhost:8086"  # URL de tu servidor InfluxDB

#     token = os.environ.get("INFLUXDB_TOKEN")
#     token="Qb1B849NA0BZRxtwv_NApXkVC_GcTwYIRJnA7IU9alSNlqeH0vF1PHsQwYe3cHR4u2tytcExzMEyuw9Tyx0fUQ=="
#     print(token)

# # Token de autenticación
#     org = "SmartHome"        # Organización en InfluxDB
#     bucket = "smartHomeData"          # Bucket donde guardarás los datos
    host=DB_HOST
    port=DB_PORT
    url=f'http://{host}:{port}'
    org=DB_ORG
    token=DB_TOKEN
    bucket=DB_BUCKET
    while intentos < 4:
        try:
            with InfluxDBClient(url=url, token=token, org=org) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)

                point = Point(topico) \
                    .tag("id_dispositivo", id) \
                    .field(sensor, mensaje) \
                    .time(datetime.utcnow(), WritePrecision.NS)
                
                write_api.write(bucket=bucket, org=org, record=point)

                print("Mensaje guardado en InfluxDB")
                return True

        except Exception as e:
            print("Error al guardar el mensaje en InfluxDB:", e)
            intentos += 1
            time.sleep(1)

    print("No se pudo guardar el mensaje después de", 4, "intentos")