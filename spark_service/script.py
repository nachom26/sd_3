import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0'

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, md5, concat_ws, col, unix_timestamp, min, max, lit, window, count
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

# Crear la sesión de Spark
spark = SparkSession.builder \
    .appName("TrafficAlertsProcessor") \
    .config("spark.cassandra.connection.host", "cassandra") \
    .config('spark.cassandra.connection.port', '9042') \
    .config("spark.cassandra.auth.username", "cassandra") \
    .config("spark.cassandra.auth.password", "cassandra") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoints") \
    .getOrCreate()

# Esquema de los datos de alerta
schema = StructType([
    StructField("type", StringType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("corner", StringType(), True),
    StructField("timestamp", TimestampType(), True)
])

# Leer el stream desde Kafka
raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "waze_alerts") \
    .load()

# Decodificar el valor del mensaje y estructurar los datos
alerts_stream = raw_stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Generar un ID único para cada alerta basado en los datos clave
alerts_stream = alerts_stream.withColumn(
    "alert_id", md5(concat_ws("-", col("type"), col("latitude"), col("longitude"), col("corner")))
)

# Agrupar alertas por tipo y por ventana de tiempo (ejemplo: 1 minuto)
grouped_alerts = alerts_stream \
    .withWatermark("timestamp", "5 minutes") \
    .groupBy(
        window(col("timestamp"), "1 minute"),  # Agrupar en ventanas de 1 minuto
        col("type")  # Agrupar por tipo de alerta
    ).agg(
        count("*").alias("alert_count")  # Contar las alertas por grupo
    )

# --- Guardar alertas activas en Elasticsearch ---
grouped_alerts.writeStream \
    .format("org.elasticsearch.spark.sql") \
    .option("es.nodes", "elasticsearch") \
    .option("es.port", "9200") \
    .option("es.resource", "grouped_alerts") \
    .outputMode("append") \
    .start()

# Escribe alertas inactivas en Cassandra
grouped_alerts.writeStream \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="historical_alerts", keyspace="traffic_data") \
    .outputMode("append").start()


# Esperar la finalización de los streams
spark.streams.awaitAnyTermination()
