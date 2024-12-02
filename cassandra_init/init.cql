-- Crear el keyspace
CREATE KEYSPACE IF NOT EXISTS traffic_data 
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

-- Usar el keyspace
USE traffic_data;

-- Crear la tabla para alertas históricas
CREATE TABLE IF NOT EXISTS alerts (
    window_start timestamp,
    window_end timestamp,
    type text,
    corner text,
    count int,
    PRIMARY KEY ((type, corner), window_start, window_end)
);