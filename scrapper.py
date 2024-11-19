from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_waze_alerts():
    # Configurar el navegador con Selenium
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.waze.com/es-419/live-map/")  # Página de Waze Live Map
    #driver.implicitly_wait(10)  # Esperar que cargue el contenido dinámico

    time.sleep(3)

    # Extraer el código HTML
    html = driver.page_source
    driver.quit()  # Cerrar el navegador

    # Analizar el HTML con BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    alerts = []

    # Buscar todos los marcadores
    for marker in soup.find_all("div", class_="leaflet-marker-icon"):
        classes = marker.get("class", [])
        for cls in classes:
            if cls.startswith("wm-alert-icon--"):
                alert = {
                    
                    "type": [cls for cls in classes if cls.startswith("wm-alert-icon--")][0].replace("wm-alert-icon--", ""),
                    
#                    "style": marker.get("style", ""),  # Incluye información de posición
                }
            elif cls.startswith("wm-alert-cluster-icon--"):
                alert = {
                    
                    "type": [cls for cls in classes if cls.startswith("wm-alert-cluster-icon--")][0].replace("wm-alert-cluster-icon--", ""),
                    
#                    "style": marker.get("style", ""),  # Incluye información de posición
                }
        alerts.append(alert)

    return alerts

def writehs(data):
    
    a = open('a.txt', 'w', encoding='utf-8')
    a.write(data)
    a.close()

if __name__ == "__main__":
    alerts = scrape_waze_alerts()
#    writehs(alerts)
    print (alerts)
#    for alert in alerts:
#        print(alert)


