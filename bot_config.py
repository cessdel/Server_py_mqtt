import logging
import telebot
import time
# Configuración del bot de Telegram
API_TOKEN = "7266018448:AAGfK6V3jROE7vL7XWjnDStlgR2WSi9u0GU"

# Instanciar el bot
bot = telebot.TeleBot(API_TOKEN)

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,  # Nivel de registro (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Formato del mensaje de registro
    handlers=[
        logging.FileHandler("bot.log"),  # Registrar en un archivo llamado "bot.log"
        logging.StreamHandler()  # Registrar también en la consola
    ]
)
# Diccionario de comandos y sus funciones asociadas
comandos = {
    '/start': lambda message: bot.reply_to(message, "Bienvenido al bot. Usa /help para ver los comandos disponibles."),
    '/help': lambda message: bot.reply_to(message, "Comandos disponibles:\n/start - Iniciar el bot\n/help - Mostrar ayuda\n/saludo - Enviar un saludo personalizado"),
    '/saludo': lambda message: bot.reply_to(message, f"Hola, {message.from_user.first_name}!")
    #'/chatid': lambda message: bot.reply_to(message, f"Tu chat ID es: {message.chat.id}")
}

# Manejador de comandos
@bot.message_handler(func=lambda message: True)
def manejar_mensaje(message):
    logging.info(f"Mensaje recibido de {message.from_user.username}: {message.text}")  # Registrar el mensaje recibido
    if message.text in comandos:
        comandos[message.text](message)
    else:
        bot.reply_to(message, "Comando no reconocido. Usa /help para ver los comandos disponibles.")




# Método para polling infinito
def infinity_polling():
    logger.info("Iniciando polling infinito")
    bot.delete_webhook()  # Asegurarse de eliminar cualquier webhook antes de iniciar el polling
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Error en polling infinito: {e}")

# Método para detener el polling
def stop_polling():
    logger.info("Deteniendo polling")
    bot.stop_polling()