import mysql.connector
from localStoragePy import localStoragePy

localStorage = localStoragePy('my_app_namespace', 'json')
# Definir variables de conexión
DB_HOST = localStorage.getItem('mysql_host')
DB_USER = localStorage.getItem('mysql_user')
DB_PASSWORD = localStorage.getItem('mysql_password')
DB_NAME = localStorage.getItem('mysql_db')


# Función para obtener la conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
