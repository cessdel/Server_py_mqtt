import asyncio
import sys
import aiomqtt
from pydantic import BaseModel
from localStoragePy import localStoragePy
from datetime import datetime, timedelta

from vars.db_config import guardar_en_influxdb

# Inicializar localStorage
localStorage = localStoragePy('my_app_namespace', 'json')
mqtt_broker = localStorage.getItem('mqtt_broker')
mqtt_port = localStorage.getItem('mqtt_port')
mqtt_topics = localStorage.getItem('mqtt_topics')

# Definir el modelo Pydantic para el JSON esperado
class TopicItem(BaseModel):
    topico: str

# Diccionario para almacenar el último valor recibido y la hora en que se recibió
last_values = {}

async def manejar_mensaje(message):
    payload = message.payload.decode('utf-8').strip("'b")
    id_dispositivo, sensor, mensaje = payload.split(":")
    mensaje = float(mensaje)

    key = (message.topic, id_dispositivo, sensor)
    current_time = datetime.now()

    if key in last_values:
        last_value, last_sent_time = last_values[key]

        # Si el valor ha cambiado, enviar inmediatamente
        if mensaje != last_value:
            guardar_en_influxdb(message.topic, id_dispositivo, sensor, mensaje)
            last_values[key] = (mensaje, current_time)
        else:
            # Si el valor no ha cambiado, verificar si han pasado 10 segundos
            if current_time - last_sent_time >= timedelta(seconds=10):
                guardar_en_influxdb(message.topic, id_dispositivo, sensor, mensaje)
                last_values[key] = (mensaje, current_time)
    else:
        # Si es la primera vez que se recibe este valor, enviarlo y guardarlo
        guardar_en_influxdb(message.topic, id_dispositivo, sensor, mensaje)
        last_values[key] = (mensaje, current_time)

async def subscribe_topics(topicos):
    async with aiomqtt.Client(hostname=mqtt_broker, port=int(mqtt_port)) as client:
        for topic_item in topicos:
            await client.subscribe(topic_item)
            print(f"Suscrito al tópico: {topic_item}")

        async for message in client.messages:
            print(f"Mensaje recibido en el tópico {message.topic}: {message.payload.decode()}")
            await manejar_mensaje(message)

        

if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    
    