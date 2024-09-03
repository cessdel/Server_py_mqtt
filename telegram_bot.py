import logging
from bot_config import bot, TELEGRAM_ID
import telebot
from telebot import types
from localStoragePy import localStoragePy


from vars.db_config import get_latest_sensor_data
logger = logging.getLogger(__name__)
localStorage = localStoragePy('my_app_namespace', 'json')


# Función para enviar mensajes a Telegram con botones
def send_alert(message: str):
    try:
        # Crear botones
        markup = types.InlineKeyboardMarkup()
        btn_lo_atiendo = types.InlineKeyboardButton("Lo atiendo", callback_data='lo_atiendo')
        btn_info = types.InlineKeyboardButton("Info", callback_data='info')
        markup.add(btn_lo_atiendo, btn_info)
        
        # Enviar mensaje con botones
        bot.send_message(chat_id=TELEGRAM_ID, text=message, reply_markup=markup)
        logger.info("Mensaje con botones enviado exitosamente.")
    except Exception as e:
        logger.error(f"Error al enviar el mensaje: {e}")

# Función para manejar la respuesta de los botones
@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    user = call.from_user
    response = call.data

    if response == 'lo_atiendo':
        # Mensaje de agradecimiento
        thank_you_message = f"🙏 Gracias, {user.first_name}! 🥰\nLa alerta ha sido atendida. ✅\n\nAquí está el menú de comandos:\n/start - Iniciar el bot\n"
        
        # Registra quién atendió la alerta
        logger.info(f"Alerta atendida por {user.username if user.username else user.first_name}.")
        
        try:
            # Enviar un nuevo mensaje con la confirmación sin intentar actualizar el mensaje original
            bot.send_message(
                chat_id=call.message.chat.id,
                text=thank_you_message
            )
            # Eliminar los botones del mensaje original
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None
            )
        except Exception as e:
            logger.error(f"Error al enviar el mensaje de agradecimiento: {e}")

    elif response == 'info':
        # Mensaje con información ficticia
        info_message = "ℹ️ Aquí tienes la información solicitada: La temperatura actual en la habitación es de 28°C. El sistema está funcionando correctamente.\n\nPor favor, selecciona una opción para continuar."
        
        try:
            # Enviar el mensaje con información
            bot.send_message(
                chat_id=call.message.chat.id,
                text=info_message
            )
            logger.info("Mensaje de información enviado.")
        except Exception as e:
            logger.error(f"Error al enviar el mensaje de información: {e}")

# Función para manejar el comando /id
@bot.message_handler(commands=['id'])
def handle_id_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    response_message = (
        f"**Tu ID de usuario:** {user_id}\n"
        f"**ID del chat:** {chat_id}"
    )
    bot.send_message(
        chat_id=message.chat.id,
        text=response_message
    )


# Función para manejar el comando /start y mostrar botones
@bot.message_handler(commands=['start'])
def start_command(message):
    # Crear botones con emojis
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    
    # Botones con texto descriptivo
    btn_info = types.KeyboardButton("ℹ️ Ayuda")
    btn_consultar = types.KeyboardButton("📊 Información en tiempo real")
    btn_prediccion = types.KeyboardButton("🔮 Predicción de Temperatura")
    
    markup.add(btn_info, btn_consultar, btn_prediccion)
    
    # Enviar mensaje con botones
    bot.send_message(
        chat_id=message.chat.id,
        text="¡Hola! Aquí están tus opciones:",
        reply_markup=markup
    )
    logger.info(f"Menú de opciones enviado a {message.from_user.username}")

# Manejador para la solicitud inicial de información en tiempo real
@bot.message_handler(func=lambda message: message.text == "📊 Información en tiempo real")
def handle_consultar(message):
    mqtt_topics = localStorage.getItem('mqtt_topics')
    if mqtt_topics:
        topicos_lista = mqtt_topics.strip('][').split(', ')
        topicos_lista = [elemento.strip("'") for elemento in topicos_lista]

        # Guardar la lista de tópicos en una variable global o en el localStorage para usarla en la próxima interacción
        localStorage.setItem('latest_topics', mqtt_topics)

        topicos_texto = "\n".join(topicos_lista)
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Escribe el nombre del sensor para obtener información:\n\n{topicos_texto}"
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="⚠️ No se encontraron tópicos disponibles."
        )

# Manejador para la solicitud de previsión
@bot.message_handler(func=lambda message: message.text == "🔮 Predicción de Temperatura")
def handle_forecast(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="🔮 Preparando la previsión de valores. Por favor, espera..."
    )
    
    # Obtener la previsión de todos los sensores
    forecast_info = get_forecast_info()

    if forecast_info:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"🔮 Previsión de valores:\n{forecast_info}"
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="⚠️ No se pudo obtener la previsión de valores."
        )

# Manejador para la solicitud de información
@bot.message_handler(func=lambda message: message.text == "ℹ️ Ayuda")
def handle_information(message):
    info_message = (
        "ℹ️ **Información del Bot**\n\n"
        "Este bot está diseñado para proporcionarte información en tiempo real sobre los sensores en tu sistema, así como previsiones futuras basadas en los datos recolectados.\n\n"
        "**Comandos disponibles:**\n"
        "/start - Inicia el bot y muestra el menú principal.\n"
        "📊 Información en tiempo real - Consulta información actual sobre los sensores.\n"
        "🔮 Predicción - Obtén previsiones de valores futuros basados en los datos de los sensores.\n\n"
        "Si tienes alguna duda o necesitas ayuda adicional, no dudes en preguntar."
    )
    bot.send_message(
        chat_id=message.chat.id,
        text=info_message
    )

# Función para obtener la previsión de valores
def get_forecast_info():
    # Implementa aquí la lógica para obtener la previsión de valores
    # utilizando tu modelo predictivo y retorna el resultado.

    # Ejemplo ficticio:
    try:
        # Aquí iría el código para obtener la predicción del modelo
        # y formatear los resultados en una cadena.
        # Esta función debería devolver una cadena de texto con la información prevista.
        
        # Supongamos que tienes una función llamada `predict_future` que retorna la predicción
        predictions = predict_future()
        return predictions
    except Exception as e:
        logger.error(f"Error al obtener la previsión de valores: {e}")
        return None

# Función de predicción futuras
def predict_future():
    # Implementa aquí la lógica para obtener las predicciones futuras
    # utilizando tu modelo predictivo y retorna el resultado.

    # Ejemplo ficticio:
    try:
        # Aquí iría el código para cargar el modelo, hacer predicciones
        # y formatear los resultados en una cadena.
        predictions = "Predicción 1: 25°C\nPredicción 2: 26°C\nPredicción 3: 27°C"
        return predictions
    except Exception as e:
        logger.error(f"Error al predecir el futuro: {e}")
        return None

# Función para manejar la solicitud de información del sensor
@bot.message_handler(func=lambda message: True)
def handle_sensor_request(message):
    # Recuperar la lista de tópicos
    mqtt_topics = localStorage.getItem('latest_topics')
    if mqtt_topics:
        topicos_lista = mqtt_topics.strip('][').split(', ')
        topicos_lista = [elemento.strip("'") for elemento in topicos_lista]

        if message.text in topicos_lista:
            latest_data = get_latest_sensor_data(message.text)

            if latest_data:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"📊 Información del sensor '{message.text}':\n{latest_data}"
                )
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"⚠️ No se pudo obtener la información para el sensor '{message.text}'."
                )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="⚠️ Sensor no reconocido. Por favor, escribe el nombre de un sensor válido."
            )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="⚠️ No se encontraron tópicos disponibles."
        )



# Función para iniciar el bot con polling infinito
def start_polling():
    logger.info("Iniciando polling infinito")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Error en polling infinito: {e}")

# Función para detener el polling
def stop_polling():
    logger.info("Deteniendo polling")
    bot.stop_polling()