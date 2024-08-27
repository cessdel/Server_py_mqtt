import logging
import telebot
from localStoragePy import localStoragePy


# Configuración del bot de Telegram
localStorage = localStoragePy('my_app_namespace', 'json')
API_TOKEN = localStorage.getItem('telegram_TOKEN')
TELEGRAM_ID = int(localStorage.getItem('telegram_ID'))

# Instanciar el bot
bot = telebot.TeleBot(API_TOKEN)
