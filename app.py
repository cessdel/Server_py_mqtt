from contextlib import asynccontextmanager
import json, logging, multiprocessing, os, asyncio
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager, contextmanager
from vars.model import FileStorage
from modelos.regression import TemperatureModel

# Inicializa la clase FileStorage
localStorage = FileStorage()
process = None

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

model_path = "model.pkl"
model_handler = TemperatureModel(model_path)
class PredictionRequest(BaseModel):
    features: list

# Ajusta el nivel de logging para 'watchfiles' a WARNING
logging.getLogger('watchfiles').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.info("Inicio de la aplicación - Verificando configuración del archivo de log")

# Configura el programador de tareas
scheduler = BackgroundScheduler()
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
        global process
        process = multiprocessing.Process(target=run_bot_polling)
        process.start()
        # Suscribirse a los tópicos
        topicos_lista = [str(topic).strip() for topic in mqtt_topics]
        asyncio.create_task(subscribe_topics(topicos_lista))
        
    else:
        logger.info("No se encontraron datos en config.json.")
        # Pausar el servidor hasta recibir la configuración
    # Verifica si el modelo ya existe
    if not os.path.exists(model_path):
        logging.info("Model not found. Training the model.")
        print("Model not found. Training the model.")
        model_handler.train_model()
        logging.info("Initial model training completed.")
    else:
        logging.info("Model found. Skipping initial training.")
        print("Model found. Skipping initial training.")
    # Agrega el trabajo al scheduler para que se ejecute a las 00:00 AM todos los días
    scheduler.add_job(model_handler.train_model, CronTrigger(hour=0, minute=0))  # Ejecuta a las 00:00 AM
    logging.info("Scheduled job to train model every day at 00:00 AM.")
    
    # Inicia el scheduler
    scheduler.start()
    yield
    process.terminate()
    process.join()
    scheduler.shutdown()
    logger.info("Server detenido")
    print("Server detenido")
    
app = FastAPI(lifespan=lifespan)
    

def run_bot_polling():  
    from telegram_bot import send_alert, start_polling, stop_polling

    try:
        print("Iniciando bot")
        start_polling()
        print("Bot iniciado")
        
    except Exception as e:
        logger.error(f"Error en el bot: {e}")
        print(f"Error en el bot: {e}")  
# Estructura JSON predeterminada


def load_config():
    config_path = 'config.json'
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
            return config_data
    else:
        return {}




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

@app.get("/status_bot")  
def status_bot():
    from bot_config import bot # Importar el bot y funciones adicionales desde bot_config
    logger.info("Verificando estado del bot")
    if bot.get_updates():
        return {"status": "activo"}  # Verificar si hay actualizaciones recientes
    else:
        return {"status": "inactivo"}
                

@app.get("/send_message")
def enviar():
    from telegram_bot import send_alert
    logger.info("Enviando mensaje de prueba")
    send_alert("Hola, soy un mensaje de prueba")

@app.get("/predict/future")
async def predict_future_temperatures():
    try:
        results = model_handler.predict_future_temperatures(hours=12)  # Predice para las próximas 12 horas
        logger.info("Future temperatures predicted.")
        return {"future_temperatures": results}
    except Exception as e:
        logger.error(f"Error predicting future temperatures: {e}")
        raise HTTPException(status_code=500, detail=f"Error predicting future temperatures: {str(e)}")

@app.get("/training-status")
async def training_status():
    logger.info("Training status")
    return {"status": model_handler.training_status}
# Función para guardar configuración en config.json
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
    global process
    if process is not None:
        process.terminate()
        process.join()
    
    process = None
    logger.info("proceso detenido")
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
        process = multiprocessing.Process(target=run_bot_polling)
        logger.info("Iniciando proceso")
        process.start()
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

