# Imagen base de Python 3.12
FROM python:3.12-slim

# Instalar dependencias necesarias para descargar y extraer Java y Cairo
RUN apt-get update && apt-get install -y wget tar libffi-dev libcairo2-dev libmagic1 && rm -rf /var/lib/apt/lists/*

# Descargar y extraer OpenJDK 23 (Temurin) - URL ACTUALIZADA
RUN wget "https://download.java.net/java/GA/jdk23.0.2/6da2a6609d6e406f85c491fcb119101b/7/GPL/openjdk-23.0.2_linux-x64_bin.tar.gz" -O /tmp/openjdk-23_linux-x64_bin.tar.gz && \
    mkdir -p /usr/local/java && \
    tar -xzf /tmp/openjdk-23_linux-x64_bin.tar.gz -C /usr/local/java --strip-components=1 && \
    rm /tmp/openjdk-23_linux-x64_bin.tar.gz

# Establecer JAVA_HOME y actualizar PATH
ENV JAVA_HOME=/usr/local/java
ENV PATH="$JAVA_HOME/bin:$PATH"

# Crear carpeta de trabajo
WORKDIR /app

# Crear el entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiamos el requirements.txt primero (mejora caché de Docker)
COPY requirements.txt .

# Instalamos dependencias Python en el venv
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiamos el resto del proyecto (incluyendo Audiveris y scripts)
COPY . .

# Damos permisos de ejecución al script (si no es un .bat)
RUN chmod +x /app/Audiveris/bin/Audiveris

# Crear directorio de logs (no en la imagen, sino en el volumen de docker-compose)
RUN mkdir -p /var/log/gunicorn && chmod -R 777 /var/log/gunicorn

# Iniciamos la app
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
