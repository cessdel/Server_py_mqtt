import asyncio
from contextlib import asynccontextmanager
import multiprocessing
import sys, os, json
import threading
from typing import List
from fastapi import FastAPI, HTTPException, Request
import databseConn
from fastapi import FastAPI
from localStoragePy import localStoragePy

from mqtt_suscriber import subscribe_topics
from vars.model import GetConfig

app = FastAPI()

subscription_active = False
topicos_lista = []
localStorage = localStoragePy('my_app_namespace', 'json')



@app.get("/active")
async def active():
    global subscription_active
    if  subscription_active==False:
        raise HTTPException(status_code=400, detail="Subscription not yet activated. Please POST to /subscribe first.")
    else:
        return {"message": "This is the /active endpoint."}

@app.get("/ping")
def ping():
    print("Ping")
    return {"message": "Servidor en línea"}

@app.on_event("startup")
async def startup_event():
    # Verificar si hay datos guardados en localStoragePy al iniciar el servidor
    if localStorage:
        data = localStorage.getItem("mqtt_broker")
        if data:
            print("Configuracion encontrada en, reiniando la suscripcion")
            mqtt_topics = localStorage.getItem('mqtt_topics')
            print(mqtt_topics)
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
    global subscription_active
    subscription_active = True
    body = await request.json()
    #SET ITEM FROM BODY
    localStorage.setItem('mqtt_broker', body["mqtt_broker"])
    localStorage.setItem('mqtt_port', body["mqtt_port"])
    localStorage.setItem('mysql_host', body["mysql_host"])
    localStorage.setItem('mysql_user', body["mysql_user"])
    localStorage.setItem('mysql_password', body["mysql_password"])
    localStorage.setItem('mysql_db', body["mysql_db"])
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
        return True
    else:
        return False


@app.get("/config")
async def returnConfig():
    c = await GetConfig()
    return c




if __name__ == "__main__":
    import uvicorn
    multiprocessing.freeze_support()
    print("-----------------Servidor iniciado----------------")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
