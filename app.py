from contextlib import asynccontextmanager
import json, logging, multiprocessing, os, asyncio
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi import FastAPI
from contextlib import asynccontextmanager, contextmanager
from vars.model import FileStorage

# Inicializa la clase FileStorage
localStorage = FileStorage()

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

# Configura el programador de tareas
subscription_active = False
topicos_lista = []

@asynccontextmanager
async def lifespan(app:FastAPI):
    
    logger.info("Server iniciado")
    # Cargar configuración del archivo config.json
    # Cargar configuración del archivo config.json
    config_data = load_config()
    
    if not config_data:
        
        logger.info("No se encontraron datos en config.json. Esperando configuración...")
        print("No se encontraron datos en config.json. Esperando configuración...")
        
        
        # Volver a cargar la configuración después de recibirla
        config_data = load_config()
    
    if config_data:
        from mqtt_suscriber import subscribe_topics
        logger.info("Configuración encontrada, reiniciando la suscripción")
        
        global subscription_active
        subscription_active = True
        # Procesar tópicos MQTT desde la configuración
        mqtt_topics = config_data.get('mqtt_topics', [])
        # Suscribirse a los tópicos
        topicos_lista = [str(topic).strip() for topic in mqtt_topics]
        asyncio.create_task(subscribe_topics(topicos_lista))
        
    else:
        logger.info("No se encontraron datos en config.json.")
        # Pausar el servidor hasta recibir la configuración

    yield
    logger.info("Server detenido")
    print("Server detenido")
    
app = FastAPI(lifespan=lifespan)
    



def load_config():
    config_path = 'config.json'
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as config_file:
                config_data = json.load(config_file)
                return config_data
        except json.JSONDecodeError as e:
            logger.error(f"Error al leer el archivo config.json: {str(e)}")
            return {}  # Devuelve un diccionario vacío si el JSON es inválido
    else:
        logger.warning(f"El archivo {config_path} no existe.")
        return {}  # Devuelve un diccionario vacío si el archivo no existe





@app.get("/active")
async def active():
    global subscription_active
    if  subscription_active==False:
        raise HTTPException(status_code=400, detail="Subscription not yet activated. Please POST to /subscribe first.")
    else:
        logger.info(" /active endpoint. ACTIVE")
        return {"message": "This is the /active endpoint."}

@app.get("/ping")
def ping():
    logger.info("Ping")
    print("Ping")
    return {"message": "Servidor en línea"}

def save_config(body):
    config_path = 'config.json'
    try:
        with open(config_path, 'w') as config_file:
            json.dump(body, config_file, indent=4)
        print("Configuración guardada en config.json")
    except Exception as e:
        logger.error(f"Error al guardar configuración: {str(e)}")
        
        
@app.post("/config")
async def CreateConfig(request: Request):
    from mqtt_suscriber import subscribe_topics
    logger.info("Configuracion recibida")
    global subscription_active
    subscription_active = True
    try:
        # Obtener el cuerpo del POST
        body = await request.json()

        # Guardar la configuración en config.json
        save_config(body)

        # Cargar datos desde el archivo JSON de configuración
        config_path = 'config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            raise FileNotFoundError("El archivo config.json no se encontró")

        # Definir las variables de conexión
        DB_PORT = config.get('influx_port')
        DB_HOST = config.get('influx_host')
        DB_ORG = config.get('influx_org')
        DB_TOKEN = config.get('influx_token')
        print("Variables de conexión:", DB_HOST, DB_PORT, DB_ORG, DB_TOKEN)


        print("Configuración guardada en config.json")
        logger.info("Configuración guardada en config.json")        
        intentarConfiguracion()
        # Procesar tópicos MQTT desde la configuración
        mqtt_topics = body.get('mqtt_topics', [])
        topicos_lista = [str(topic).strip() for topic in mqtt_topics]
        print("Subscribing to topics:", topicos_lista)
        asyncio.create_task(subscribe_topics(topicos_lista))
        logger.info("Iniciando proceso")
        return {"message": "Configuración recibida", "data": body}
    
    except KeyError as e:
        logger.error(f"Falta un campo en la configuración: {str(e)}")
        return {"message": "Error en la configuración", "error": str(e)}

    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return {"message": "Error inesperado", "error": str(e)}
    

def intentarConfiguracion():
    import databseConn
    
    if databseConn.verificar_conexion() and databseConn.verificar_conexion_internet():
        logger.info("Conexión a la base de datos y a internet exitosa")
        return True
    else:
        logger.error("Error en la conexión a la base de datos o a internet")
        return False
    
    

@app.get("/config")
async def returnConfig():
    logger.info("Enviando configuracion")
    c = load_config()
    return c

if __name__ == "__main__":
    import uvicorn
    multiprocessing.freeze_support()
    print("-----------------Servidor iniciado----------------")
    logger.info("Servidor iniciado")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

