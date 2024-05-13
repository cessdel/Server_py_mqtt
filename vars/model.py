from localStoragePy import localStoragePy


localStorage = localStoragePy('my_app_namespace', 'json')


async def GetConfig():
    mqtt_broker = localStorage.getItem('mqtt_broker')
    mqtt_port = localStorage.getItem('mqtt_port')
    mysql_host = localStorage.getItem('mysql_host')
    mysql_user = localStorage.getItem('mysql_user')
    mysql_password = localStorage.getItem('mysql_password')
    mysql_db = localStorage.getItem('mysql_db')
    mqtt_topics = localStorage.getItem('mqtt_topics')
    return {"message": "Se obtuvo la configuracion", "data": {"mqtt_broker": mqtt_broker, "mqtt_port": mqtt_port, "mysql_host": mysql_host, "mysql_user": mysql_user, "mysql_password": mysql_password, "mysql_db": mysql_db, "mqtt_topics": mqtt_topics}}
