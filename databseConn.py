import datetime
import logging
import time

import requests


MAX_INTENTOS = 3  # Número máximo de intentos de conexión

#verificar_conexion_internet()
def verificar_conexion_internet():
    intentos = 0
    while intentos < MAX_INTENTOS:
        try:
            requests.get("http://www.google.com", timeout=5)
            print("Conexión a Internet exitosa")
            logging.info("Conexión a Internet exitosa")
            return True
        except requests.ConnectionError:
            logging.info("Error al conectar a Internet. Reintentando...")
            print("Error al conectar a Internet. Reintentando...")
            intentos += 1
            time.sleep(1)
    print("No se pudo establecer conexión a Internet después de", MAX_INTENTOS, "intentos")
    return False
def verificar_conexion():
    from vars.db_config import check_influxdb_connection
    intentos = 0
    while intentos < MAX_INTENTOS:
        try:
            # Establecer conexión con la base de datos MySQL
            connection = check_influxdb_connection()

            # Verificar si la conexión fue exitosa
            if connection==True:
                print("Conexión exitosa a la base de datos")
                logging.info("Conexión exitosa a la base de datos")
                return True
            else:
                print("Error al conectar a la base de datos")
                logging.info("Error al conectar a la base de datos")
                intentos += 1
                time.sleep(1)  # Esperar un segundo antes de intentar de nuevo

            # Cerrar conexión
            connection.close()
        except Exception as e:
            print("Error al conectar a la base de datos:", e)
            intentos += 1
            time.sleep(1)  # Esperar un segundo antes de intentar de nuevo
            logging.info("Error al conectar a la base de datos. Reintentando...")
            
    print("No se pudo establecer conexión después de", MAX_INTENTOS, "intentos")
    logging.info("No se pudo establecer conexión después de", MAX_INTENTOS, "intentos")
    return False

