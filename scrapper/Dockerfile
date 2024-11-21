# Usar una imagen base de Python
FROM python:3.10

# Instalar las dependencias del sistema necesarias para Chrome y Selenium
RUN apt-get update -qq -y && \
    apt-get install -y \
        libasound2 \
        libatk-bridge2.0-0 \
        libgtk-4-1 \
        libnss3 \
        xdg-utils \
        wget \
        unzip \
        jq

    RUN wget -q -O chrome-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.85/linux64/chrome-linux64.zip && \
    unzip chrome-linux64.zip && \
    rm chrome-linux64.zip && \
    mv chrome-linux64 /opt/chrome/ && \
    ln -s /opt/chrome/chrome /usr/local/bin/ && \
    wget -q -O chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.85/linux64/chromedriver-linux64.zip && \
    unzip -j chromedriver-linux64.zip chromedriver-linux64/chromedriver && \
    rm chromedriver-linux64.zip && \
    mv chromedriver /usr/local/bin/

# Configurar variables de entorno para ChromeDriver
ENV PATH="/usr/local/bin:$PATH"

# Copiar el archivo requirements.txt
COPY requirements.txt /app/requirements.txt

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar el script al contenedor
COPY . /app

# Establecer el directorio de trabajo
WORKDIR /app

RUN chrome --version && chromedriver --version

# Comando por defecto para ejecutar el script
CMD ["python", "scrapper.py"]
