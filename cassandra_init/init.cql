-- Crear el keyspace
CREATE KEYSPACE IF NOT EXISTS traffic_data 
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

-- Usar el keyspace
USE traffic_data;

-- Crear la tabla para alertas históricas
CREATE TABLE IF NOT EXISTS historical_alerts (
    alert_id TEXT PRIMARY KEY,
    type TEXT,
    latitude DOUBLE,
    longitude DOUBLE,
    corner TEXT,
    timestamp TIMESTAMP
);
