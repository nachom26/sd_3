# Usar una imagen oficial de Spark
FROM bitnami/spark:3.2.0

# Instalar Python y pip
USER root
RUN apt-get update && apt-get install -y python3-pip python3-dev

# Establecer directorio de trabajo
WORKDIR /spark_service

# Copiar el script y las dependencias al contenedor
COPY script.py /spark_service/
COPY requirements.txt /spark_service/

# Instalar dependencias de Python
RUN pip3 install --no-cache-dir -r /spark_service/requirements.txt

# Configurar Spark para usar los conectores necesarios
ENTRYPOINT ["spark-submit",\
    "--master", "local[*]", \
    "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,com.datastax.spark:spark-cassandra-connector_2.12:3.2.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.16.1", \
    "/spark_service/script.py"]

