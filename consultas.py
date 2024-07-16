
from datetime import datetime
import time,os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

def guardar_en_influxdb(topico, id, sensor, mensaje):
#     intentos = 0
    
#     # Configuración de InfluxDB (reemplaza con tus datos)
#     url = "http://localhost:8086"  # URL de tu servidor InfluxDB

#     token = os.environ.get("INFLUXDB_TOKEN")
#     token="Qb1B849NA0BZRxtwv_NApXkVC_GcTwYIRJnA7IU9alSNlqeH0vF1PHsQwYe3cHR4u2tytcExzMEyuw9Tyx0fUQ=="
#     print(token)

# # Token de autenticación
#     org = "SmartHome"        # Organización en InfluxDB
#     bucket = "smartHomeData"          # Bucket donde guardarás los datos

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
    return False

guardar_en_influxdb("temperatura", "sensor1", "temperatura", 20.00)