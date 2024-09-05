import logging
from influxdb_client import InfluxDBClient, Point, QueryApi
from influxdb_client.client.exceptions import InfluxDBError
from datetime import datetime
import time,os,json
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS






#Funcion para obtener los datos de los sensores
def get_latest_sensor_data(topic: str) -> str:
    config_path = 'config.json'
# Cargar datos desde el archivo JSON de configuración
    with open(config_path, 'r') as f:
        config = json.load(f)

    
    # Definir variables de conexión
    DB_PORT = config.get('influx_port')
    DB_HOST = config.get('influx_host')
    DB_ORG = config.get('influx_org')
    DB_TOKEN = config.get('influx_token')
    DB_BUCKET = config.get('influx_bucket')
    url=f'http://{str(DB_HOST)}:{str(DB_PORT)}'

    client = InfluxDBClient(url, token=DB_TOKEN, org=DB_ORG)
    query_api = client.query_api()
    query = f"""
    from(bucket: "{DB_BUCKET}")
    |> range(start: -1h)
    |> filter(fn: (r) => r._measurement == "{topic}")
    |> last()
    """
    
    #print("Consulta Flux:", query)  # Imprimir consulta para depuración
    
    try:
        tables = query_api.query(query, org=DB_ORG)
        result = ""
        
        for table in tables:
            for record in table.records:
                result = (f"Último dato para {topic}:\n"
                        f"Valor: {record.get_value()} {record.get_field()}\n"
                        f"Fecha: {record.get_time()}")
                return result
        logging.error(f"No se encontró información para {topic}")
        return f"No se encontró información para {topic}"
    
    except Exception as e:
        logging.error(f"Error al consultar la información de {topic}: {e}")
        print(f"Error al consultar la información de {topic}: {e}")
        return "Error al consultar la información."
    

# Cierra el cliente después de realizar todas las consultas necesarias
def close_client():
    config_path = 'config.json'
    # Cargar datos desde el archivo JSON de configuración
    with open(config_path, 'r') as f:
        config = json.load(f)

    
    # Definir variables de conexión
    DB_PORT = config.get('influx_port')
    DB_HOST = config.get('influx_host')
    DB_ORG = config.get('influx_org')
    DB_TOKEN = config.get('influx_token')
    DB_BUCKET = config.get('influx_bucket')
    url=f'http://{str(DB_HOST)}:{str(DB_PORT)}'

    client = InfluxDBClient(url, token=DB_TOKEN, org=DB_ORG)
    query_api = client.query_api()
    client.close()


# Función para obtener la conexión a la base de datos
import json

def check_influxdb_connection():
    config_path = 'config.json'
# Cargar datos desde el archivo JSON de configuración
    with open(config_path, 'r') as f:
        config = json.load(f)

    
    # Definir variables de conexión
    DB_PORT = config.get('influx_port')
    DB_HOST = config.get('influx_host')
    DB_ORG = config.get('influx_org')
    DB_TOKEN = config.get('influx_token')
    DB_BUCKET = config.get('influx_bucket')
    # Asegurarse de que se han obtenido los valores
    print("Variables de conexión:", DB_HOST, DB_PORT, DB_ORG, DB_TOKEN)
    
    # Crear URL para conectar a InfluxDB
    url = f'http://{str(DB_HOST)}:{str(DB_PORT)}'
    
    try:
        # Intentar conectarse a InfluxDB
        client = InfluxDBClient(url, str(DB_TOKEN), DB_ORG)
        health = client.health()
        
        if health.status == "pass":
            print("Conexión exitosa.")
            return True
        else:
            print(f"Conexión fallida: {health.message}")
            return False
    except InfluxDBError as e:
        print(f"Ocurrió un error con InfluxDB: {e}")
        return False
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return False


def guardar_en_influxdb(topico, id, sensor, mensaje):
    intentos = 0
    config_path = 'config.json'
# Cargar datos desde el archivo JSON de configuración
    with open(config_path, 'r') as f:
        config = json.load(f)

    
    # Definir variables de conexión
    DB_PORT = config.get('influx_port')
    DB_HOST = config.get('influx_host')
    DB_ORG = config.get('influx_org')
    DB_TOKEN = config.get('influx_token')
    DB_BUCKET = config.get('influx_bucket')
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
                        .tag("sensor", sensor) \
                            .field("valor", mensaje) \
                                .time(datetime.utcnow(), WritePrecision.NS)
                
                write_api.write(bucket=bucket, org=org, record=point)

                print("Mensaje guardado en InfluxDB")
                return True

        except Exception as e:
            print("Error al guardar el mensaje en InfluxDB:", e)
            intentos += 1
            time.sleep(1)

    print("No se pudo guardar el mensaje después de", 4, "intentos")