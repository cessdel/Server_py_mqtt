# Usa una imagen base de Python optimizada
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de tu aplicación al contenedor
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que la aplicación correrá
EXPOSE 8000

# Comando para ejecutar el archivo main.py que ya contiene la lógica de uvicorn
CMD ["python", "app.py"]
