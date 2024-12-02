# Sistema de Scrapping de Waze y Procesamiento de Alertas

Este sistema es una aplicación distribuida para hacer scrapping de alertas del live map de Waze, las cuales luego se procesan y se almacenan para su futuro analisis.

## Estructura de la Aplicación

1. **Scrapper**:
    - Recopila los datos de la pagina [Waze](https://www.waze.com/es-419/live-map/) para luego extraer las alertas publicadas en Santiago de Chile.
    - Separa la ciudad en 4 áreas distintas para poder recopilar la mayor cantidad de alertas posible.
    - Envia los datos a Kafka para su posterior procesamiento y analisis.

2. **Procesamiento de datos (Spark)**:
    - Recibe los datos enviados desde Kafka y los agrupa por tipo de alerta, sección de la ciudad en la que se publicó y minuto en el que se extrajp.
    - Envia los datos procesados a ElasticSearch y Cassandra.

## Tecnologías Utilizadas

- **Docker**: Conteneriza todos los servicios y simplificar la implementación.
- **Selenium**: Automatizacion de pruebas en aplicaciones web por medio de varios navegadores.
- **BeautifulSoup**: Recupera el HTML dejado por Selenium y extrae los datos. Herramienta principal para el scrapping.
- **Kafka**: Mensajería entre contenedores.
- **Elasticsearch y Kibana**: Almacenamiento y visualización de alertas en tiempo real.
- **Cassandra**: Almacenamiento y analisis de alertas a nivel histórico.
- **Spark**: Procesamiento de datos a gran escala en clústeres.

## Instrucciones de Instalación

1. **Clonar el repositorio**:
    ```bash
    git clone https://github.com/nachom26/sd_3.git
    cd sd_3

2. **Inicia los servicios con docker compose**:
    ```bash
    docker-compose up

3. **Acceso a los servicios**:
    - **Kibana**: Accede a http://localhost:5601
    - **Cassandra**: Desde la terminal en la carpeta del repositorio, ejecutar
        ```bash
        docker exec -it cassandra bash

        cqlsh cassandra -u cassandra -p cassandra
