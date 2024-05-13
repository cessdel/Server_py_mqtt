import sys, os
from typing import List
from fastapi import FastAPI, HTTPException, Request
import databseConn

from mqtt_suscriber import TopicItem, subscribe_topics

from localStoragePy import localStoragePy


app = FastAPI()

subscription_active = False

localStorage = localStoragePy('my_app_namespace', 'json')


@app.post("/subscribe/")
async def handle_subscription(topics: List[TopicItem]):
    global subscription_active
    subscription_active = True
    result = await subscribe_topics(topics)
    return result


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


@app.post("/MqttConfig")
async def CreateConfig(request: Request):
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
    return {"message": "Configuracion recibida", "data": body}

@app.get("/MqttConfig")
def GetConfig():
    mqtt_broker = localStorage.getItem('mqtt_broker')
    mqtt_port = localStorage.getItem('mqtt_port')
    mysql_host = localStorage.getItem('mysql_host')
    mysql_user = localStorage.getItem('mysql_user')
    mysql_password = localStorage.getItem('mysql_password')
    mysql_db = localStorage.getItem('mysql_db')
    mqtt_topics = localStorage.getItem('mqtt_topics')
    return {"message": "Se obtuvo la configuracion", "data": {"mqtt_broker": mqtt_broker, "mqtt_port": mqtt_port, "mysql_host": mysql_host, "mysql_user": mysql_user, "mysql_password": mysql_password, "mysql_db": mysql_db, "mqtt_topics": mqtt_topics}}

    
if __name__ == "__main__":
    import uvicorn
    print("-----------------Servidor iniciado----------------")
    # Verificar la conexión a la base de datos y a internet
    #databseConn.verificar_conexion()
    #databseConn.verificar_conexion_internet()
    print("Esperando mensajes MQTT...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
