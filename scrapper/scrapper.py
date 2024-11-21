from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import re
from concurrent.futures import ThreadPoolExecutor
from kafka import KafkaProducer
import json

#extrae las coordenadas de la alerta en el mapa, esta esta guardada como translate3d(x, y) en el estilo, se necesitan x e y 
def extract_coordinates(style):
    match = re.search(r'translate3d\(([^,]+),\s*([^,]+),', style)
    if match:
        return {"x": float(match.group(1).replace('px', '')), "y": float(match.group(2).replace('px', ''))}
    return None  # Si no coincide con el patrón

#enviar alertas a kafka
def send_to_kafka(alerts):
    producer = KafkaProducer(
        bootstrap_servers=['kafka:9092'],  # Cambia a la dirección de tu clúster Kafka
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    for alert in alerts:
        producer.send('waze_alerts', alert)
    producer.flush()
    print("alertas enviadas")

#scrapping de una esquina especificada
def scrape_corner(value, corner_name):

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options) #se usa la instalacion local de chrome y chromedriver
    key = "livemapMapPosition"
    
    driver.get("https://www.waze.com/es-419/live-map/")
    time.sleep(2)
    driver.execute_script(f"window.localStorage.setItem('{key}','{value}')")
    time.sleep(2)
    driver.refresh()
    time.sleep(2)
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    alerts = []

    # Buscar todos los marcadores
    for marker in soup.find_all("div", class_="leaflet-marker-icon"):
        classes = marker.get("class", [])
        for cls in classes:
            if cls.startswith("wm-alert-icon--"):
                alert = {
                    "type": [cls for cls in classes if cls.startswith("wm-alert-icon--")][0].replace("wm-alert-icon--", ""),
                    "style": extract_coordinates(marker.get("style", "")),
                    "corner": corner_name,
                    "timestamp": time.time()
                }
                alerts.append(alert)
            elif cls.startswith("wm-alert-cluster-icon--"):
                alert = {
                    "type": [cls for cls in classes if cls.startswith("wm-alert-cluster-icon--")][0].replace("wm-alert-cluster-icon--", ""),
                    "style": extract_coordinates(marker.get("style", "")),
                    "corner": corner_name,
                    "timestamp": time.time()
                }
                alerts.append(alert)

    return alerts

def scrape_waze_alerts_parallel():
    # Valores de localStorage para cada esquina
    corners = {
        "bottom_left": ' { "value": "-70.73620319366456,-33.49867548541488,-70.68998336791994,-33.46545873876678", "expires": 1734649008597, "version": "0.0.0" }',
        "top_left": '{ "value": "-70.74238300323488,-33.42742998368805,-70.69616317749025,-33.39418593758076", "expires": 1734650266912, "version": "0.0.0" }',
        "top_right": '{ "value": "-70.58376789093019,-33.42220062164151,-70.53754806518556,-33.38895457380163", "expires": 1734650297264, "version": "0.0.0" }',
        "bottom_right": '{ "value": "-70.59226512908937,-33.48851136814119,-70.54604530334474,-33.45529072371885", "expires": 1734650320123, "version": "0.0.0" }'
    }

    # Ejecutar el scraping en paralelo
    alerts = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_corner, value, corner_name) for corner_name, value in corners.items()]
        for future in futures:
            alerts.extend(future.result())

    return alerts

if __name__ == "__main__":
    while(True):
        alerts = scrape_waze_alerts_parallel()
#        print(alerts)
        send_to_kafka(alerts)
        time.sleep(300)