from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Configurar el servicio de ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Navegar a la página de Wikipedia de los pueblos indígenas de México
url = "https://es.m.wikipedia.org/wiki/Pueblos_ind%C3%ADgenas_de_M%C3%A9xico"
driver.get(url)

# Esperar a que el section se cargue utilizando una espera explícita
try:
    section = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'content-collapsible-block-8'))
    )

    # Encontrar la tabla dentro del section utilizando un selector CSS más específico
    table = section.find_element(By.CSS_SELECTOR, 'table.sortable.striped.col3der.jquery-tablesorter')

    # Extraer todas las filas de la tabla
    rows = table.find_elements(By.TAG_NAME, "tr")

    # Extraer los encabezados
    headers = [header.text for header in rows[0].find_elements(By.TAG_NAME, "th")]
    print("Encabezados:", headers)

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

    # Nombre del archivo CSV donde se guardará el DataFrame
    csv_file = "pueblos_indigenas_mexico.csv"

    # Guardar el DataFrame en CSV
    df.to_csv(csv_file, index=False)  # index=False para no incluir el índice en el archivo CSV

except Exception as e:
    print(f"Error: {e}")

finally:
    # Cerrar el navegador al finalizar
    driver.quit()
