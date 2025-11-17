# Paso 1: Usar una imagen base de Python ligera (Recomendado para entornos de producción) 

 
FROM python:3.10-slim 
 
# Paso 2: Establecer el directorio de trabajo dentro del contenedor 
WORKDIR /app 
 
# Paso 3: Copiar el archivo de requisitos y las configuraciones 
# Esto permite que Docker use el cache si requirements.txt no cambia 
COPY requirements.txt . 
 
# Paso 4: Instalar las dependencias de Python 
# Se usa --no-cache-dir para mantener la imagen más pequeña 
RUN pip install --no-cache-dir -r requirements.txt 
 
# Paso 5: Copiar el código fuente de la aplicación (api.py y src/) 
# Se copia todo el código de la aplicación y el módulo src 
COPY . /app 
 
# NOTA IMPORTANTE: Asegúrate de que el modelo y los preprocesadores 
# (models/encoders/*.pkl y models/preprocessors/*.pkl) se copien 
# junto con el resto del proyecto en el COPY . /app 
 
# Paso 6: Exponer el puerto donde se ejecutará FastAPI (por defecto: 8000) 
EXPOSE 8000 
 
# Paso 7: Definir el comando de inicio para ejecutar la API 
# Se usa Uvicorn con Gunicorn para un rendimiento robusto en producción. 
# El comando ejecuta el módulo api, la aplicación 'app' y define el puerto 8000. 
# Ajusta los workers (-w) según la cantidad de CPUs disponibles para el contenedor. 
CMD ["gunicorn", "api:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"] 
 