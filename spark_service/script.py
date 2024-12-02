#import os
#os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0'
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, md5, concat_ws, col, unix_timestamp, min, max, lit, window, count, to_timestamp, from_unixtime
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
import time


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
    StructField("corner", StringType(), True),
    StructField("timestamp", DoubleType(), True)
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

alerts_stream = alerts_stream.withColumn(
    "timestamp",
    to_timestamp(from_unixtime(col("timestamp")))  # Convierte epoch a timestamp
)
"""
alerts_stream.writeStream \
    .format("console") \
    .outputMode("append") \
    .start()
"""
# Agrupar alertas por tipo y por ventana de tiempo (ejemplo: 1 minuto)
grouped_alerts = alerts_stream \
    .withWatermark("timestamp", "1 hour") \
    .groupBy(
        ["type",  # Agrupar por tipo de alerta
        "corner",
        window("timestamp", "1 minutes")]
    ).count() \
    .withColumn("window_start", col("window").start) \
    .withColumn("window_end", col("window").end) \
    .drop("window")



grouped_alerts.writeStream \
    .format("console") \
    .outputMode("complete") \
    .start()

    
"""
# --- Guardar alertas activas en Elasticsearch ---
grouped_alerts.writeStream \
    .format("org.elasticsearch.spark.sql") \
    .option("es.nodes", "elasticsearch") \
    .option("es.port", "9200") \
    .option("es.resource", "grouped_alerts") \
    .outputMode("append") \
    .start()
"""

from pyspark.sql.functions import col

def write_to_cassandra(batch_df, batch_id):
#    time.sleep(5)

    print(f"escribiendo {batch_df.count()} a cassandra")

    try:
        batch_df.write \
            .format("org.apache.spark.sql.cassandra") \
            .options(table="alerts", keyspace="traffic_data") \
            .mode("append") \
            .save()
    except Exception as e:
        print(f"Error al escribir en Cassandra en el lote {batch_id}: {e}")

    

def write_to_elastic(batch_df, batch_id):
#    time.sleep(5)

    print(f"escribiendo {batch_df.count()} a elastic")
    try:
        batch_df.write \
            .format("org.elasticsearch.spark.sql") \
            .option("es.nodes", "elasticsearch") \
            .option("es.port", "9200") \
            .option("es.resource", "grouped_alerts") \
            .mode("append") \
            .save()
    except Exception as e:
        print(f"Error al escribir en Elastic en el lote {batch_id}: {e}")

w= grouped_alerts.writeStream \
    .foreachBatch(write_to_cassandra) \
    .outputMode("complete") \
    .start()

w2= grouped_alerts.writeStream \
    .foreachBatch(write_to_elastic) \
    .outputMode("complete") \
    .start()

"""
# Escribe alertas inactivas en Cassandra
grouped_alerts.writeStream \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="alerts", keyspace="traffic_data") \
    .outputMode("append").start()
"""


"""
for query in spark.streams.active:
    print(f"Nombre de la consulta: {query.name}")
    print(f"Progreso: {query.lastProgress}")
    print(f"Estado: {query.status}")
"""
spark.sparkContext.setLogLevel("WARN")

# Esperar la finalización de los streams
spark.streams.awaitAnyTermination()