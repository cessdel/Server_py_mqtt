import asyncio
import aiomqtt,os, sys
from pydantic import BaseModel
import databseConn
from localStoragePy import localStoragePy

localStorage = localStoragePy('my_app_namespace', 'json')
mqtt_broker = localStorage.getItem('mqtt_broker')
mqtt_port = localStorage.getItem('mqtt_port')
mqtt_topics = localStorage.getItem('mqtt_topics')

# Definir el modelo Pydantic para el JSON esperado
class TopicItem(BaseModel):
    topico: str
    

async def subscribe_topics(topicos):
    async with aiomqtt.Client(hostname= mqtt_broker, port= int(mqtt_port)) as client:
        for topic_item in topicos:
            await client.subscribe(topic_item)
            print(f"Suscrito al tópico: {topic_item}")

        async for message in client.messages:
            print(f"Mensaje recibido en el tópico {message.topic}: {message.payload.decode()}")
            #guardar_en_mysql(message.payload.decode())
            payload = message.payload.decode('utf-8').strip("'b")  # Convertir el payload a cadena de texto
            id_dispositivo,sensor, mensaje = payload.split(":")
            print("Id    ",id_dispositivo)# Separar el ID del dispositivo y el mensaje
            print("Mensaje    ",mensaje)
            print("Sensor    ",sensor)
            print(message.topic)
            databseConn.guardar_en_mysql(message.topic,id_dispositivo,sensor,mensaje)
        

if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    
    