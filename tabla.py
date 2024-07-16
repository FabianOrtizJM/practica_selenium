from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import json

# Configurar el servicio de ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Navegar a la página de Wikipedia
url = "https://es.wikipedia.org/wiki/Poblaci%C3%B3n_ind%C3%ADgena_de_Colombia"
driver.get(url)

# Esperar a que la página se cargue
time.sleep(3)

# Encontrar la tabla en la página utilizando XPath
table = driver.find_element(By.CSS_SELECTOR, "div#mw-content-text > div > table.wikitable")


# Extraer todas las filas de la tabla
rows = table.find_elements(By.TAG_NAME, "tr")

# Extraer los encabezados
headers = [header.text for header in rows[0].find_elements(By.TAG_NAME, "th")]

# Extraer los datos de cada fila
data = []
for row in rows[1:]:
    cols = row.find_elements(By.TAG_NAME, "td")
    cols = [col.text for col in cols]
    data.append(cols)

# Crear un DataFrame con los datos extraídos
df = pd.DataFrame(data, columns=headers)


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Mostrar el DataFrame
print(df)

ruta_archivo = 'C:/Users/garfi/OneDrive/Escritorio/tabla_poblacion_indigena_colombia.xlsx'
df.to_excel(ruta_archivo, index=False)

# Cerrar el navegador
driver.quit()
