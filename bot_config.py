import telebot
import time
# Configuración del bot de Telegram
API_TOKEN = "7266018448:AAGfK6V3jROE7vL7XWjnDStlgR2WSi9u0GU"

#instanciar el bot
bot = telebot.TeleBot(API_TOKEN)

# Diccionario de comandos
def cmd_start(message):
    bot.reply_to(message, "Hola! Soy tu bot de smart home. Usa /help para ver los comandos.")

def cmd_help(message):
    bot.reply_to(message, """
Comandos disponibles:
/start - Iniciar el bot
/help - Mostrar esta ayuda
/estado - Ver estado de los sensores
/configurar - Ajustar configuraciones (próximamente)
""")

def cmd_estado(message):
    try:
        temperatura = obtener_temperatura()
        humedad = obtener_humedad()
        # ... (obtener otros datos de sensores)

        mensaje = f"Estado actual:\nTemperatura: {temperatura}°C\nHumedad: {humedad}%"
        # ... (agregar más datos al mensaje)
        bot.reply_to(message, mensaje)
    except Exception as e:
        bot.reply_to(message, "Error al obtener datos de los sensores.")
        print(f"Error en cmd_estado: {e}")

comandos = {
    '/start': cmd_start,
    '/help': cmd_help,
    '/estado': cmd_estado,
}

# Manejador de comandos
@bot.message_handler(commands=list(comandos.keys()))
def handle_command(message):
    comando = message.text.lower()
    if comando in comandos:
        comandos[comando](message)
    else:
        bot.reply_to(message, "Comando no reconocido. Usa /help para ver los comandos disponibles.")

# Función para enviar mensajes (con manejo de errores)
def send_message(chat_id: int, message: str):
    try:
        bot.send_message(chat_id, message)
        print(f"Mensaje enviado a {chat_id}: {message}")
    except telebot.apihelper.ApiException as e:
        print(f"Error de Telegram al enviar mensaje: {e}")
    except Exception as e:
        print(f"Error general al enviar mensaje: {e}")