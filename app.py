import asyncio
from contextlib import asynccontextmanager
import logging
import multiprocessing
import sys, os, json
import threading
from typing import List
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
import databseConn
from fastapi import FastAPI
from localStoragePy import localStoragePy
from mqtt_suscriber import subscribe_topics
from telegram_bot import send_alert
from vars.model import GetConfig
from bot_config import bot # Importar el bot y funciones adicionales desde bot_config
import telebot

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

# Ajusta el nivel de logging para 'watchfiles' a WARNING
logging.getLogger('watchfiles').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.info("Inicio de la aplicación - Verificando configuración del archivo de log")


app = FastAPI()

subscription_active = False
topicos_lista = []
localStorage = localStoragePy('my_app_namespace', 'json')

def run_bot_polling():  
    try:
        print("Bot corriendo")
        bot.infinity_polling()  
        
    except Exception as e:
        print(f"Error en el bot: {e}")  
        



@app.get("/active")
async def active():
    global subscription_active
    if  subscription_active==False:
        raise HTTPException(status_code=400, detail="Subscription not yet activated. Please POST to /subscribe first.")
    else:
        return {"message": "This is the /active endpoint."}

@app.get("/ping")
def ping():
    logger.info("Ping")
    print("Ping")
    return {"message": "Servidor en línea"}

@app.get("/status_bot")  
def status_bot():
    logger.info("Verificando estado del bot")
    if bot.get_updates():
        return {"status": "activo"}  # Verificar si hay actualizaciones recientes
    else:
        return {"status": "inactivo"}
                

@app.get("/send_message")
def enviar():
    logger.info("Enviando mensaje de prueba")
    send_alert("Hola, soy un mensaje de prueba")

@app.on_event("startup")
async def startup_event():
    process = multiprocessing.Process(target=run_bot_polling)
    process.start()
    logger.info("Bot iniciado")

    
    # Verificar si hay datos guardados en localStoragePy al iniciar el servidor
    if localStorage:
        data = localStorage.getItem("mqtt_broker")
        if data:
            logger.info("Configuracion encontrada en, reiniando la suscripcion")
            print("Configuracion encontrada en, reiniando la suscripcion")
            global subscription_active 
            subscription_active = True
            print("Subscription active: ", subscription_active)
            mqtt_topics = localStorage.getItem('mqtt_topics')
            print(mqtt_topics)
            DBstatus = intentarConfiguracion()
            topicos_lista = mqtt_topics.strip('][').split(', ')
            topicos_lista = [elemento.strip("'") for elemento in topicos_lista]
            #SUBSCRIBE TO TOPICS
            #await subscribe_topics(topicos_lista)
            asyncio.create_task(subscribe_topics(topicos_lista))
                    
        else:
            print("No se encontraron datos en localStoragePy.")
    else:
        print("No se pudo acceder a localStoragePy.")
    
    

@app.post("/config")
async def CreateConfig(request: Request):
    logger.info("Configuracion recibida")
    global subscription_active
    subscription_active = True
    body = await request.json()
    #SET ITEM FROM BODY
    localStorage.setItem('mqtt_broker', body["mqtt_broker"])
    localStorage.setItem('mqtt_port', body["mqtt_port"])
    localStorage.setItem('influx_host', body["influx_host"])
    localStorage.setItem('influx_port', body["influx_port"])
    localStorage.setItem('influx_token', body["influx_token"])
    localStorage.setItem('influx_org', body["influx_org"])
    localStorage.setItem('influx_bucket', body["influx_bucket"])
    localStorage.setItem('telegram_TOKEN', body["telegram_TOKEN"])
    localStorage.setItem('telegram_ID', body["telegram_ID"])
    localStorage.setItem('mqtt_topics', body["mqtt_topics"])
    print("Configuracion recibida")
    print("Probando configuracion")
    # Verificar la conexión a la base de datos y a internet
    intentarConfiguracion()
    mqtt_topics = localStorage.getItem('mqtt_topics')
    print(mqtt_topics)
    topicos_lista = mqtt_topics.strip('][').split(', ')
    topicos_lista = [elemento.strip("'") for elemento in topicos_lista]
    #SUBSCRIBE TO TOPICS
    #await subscribe_topics(topicos_lista)
    asyncio.create_task(subscribe_topics(topicos_lista))
    return {"message": "Configuracion recibida", "data": body}
def intentarConfiguracion():
    
    if databseConn.verificar_conexion() and databseConn.verificar_conexion_internet():
        logger.info("Conexión a la base de datos y a internet exitosa")
        return True
    else:
        logger.error("Error en la conexión a la base de datos o a internet")
        return False


@app.get("/config")
async def returnConfig():
    logger.info("Enviando configuracion")
    c = await GetConfig()
    return c

if __name__ == "__main__":
    import uvicorn
    multiprocessing.freeze_support()
    print("-----------------Servidor iniciado----------------")
    logger.info("Servidor iniciado")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

