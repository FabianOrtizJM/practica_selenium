from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import json


class ExtraccionProductos:
    def __init__(self, config_file):
        self.driver = None
        self.data = self.load_config(config_file)
        self.products_data = []

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            data = json.load(file)
        return data

    def setup_driver(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def buscar_extraer(self):
        url = self.data['website']
        self.driver.get(url)
        time.sleep(3)

        for search_term_data in self.data['search_terms']:
            search_term = search_term_data['term']
            selectors = search_term_data['selectors']

            search_bar = self.driver.find_element(By.ID, self.data['search_input'])
            search_bar.clear()
            search_bar.send_keys(search_term)
            search_bar.send_keys(Keys.RETURN)
            time.sleep(3)

            products = self.driver.find_elements(By.CSS_SELECTOR, selectors['container'])
            for product in products:
                try:
                    product_title = product.find_element(By.CSS_SELECTOR, selectors['title']).text
                    product_price = product.find_element(By.CSS_SELECTOR, selectors['price_whole']).text
                    product_price_fraction = product.find_element(By.CSS_SELECTOR, selectors['price_fraction']).text
                    price = product_price + '.' + product_price_fraction

                    self.products_data.append([product_title, price])
                except Exception as e:
                    continue

    def save_to_excel(self, file_path):
        df = pd.DataFrame(self.products_data, columns=['Producto', 'Precio'])
        df = df.sort_values(by='Precio', ascending=False)
        df.to_excel(file_path, index=False)

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

        print(df)

        pd.reset_option('display.max_rows')
        pd.reset_option('display.max_columns')
        pd.reset_option('display.width')
        pd.reset_option('display.max_colwidth')


def main():
    config_file = 'amazon.json'
    file_path = 'C:/Users/garfi/OneDrive/Escritorio/productos_amazon.xlsx'

    Extraer = ExtraccionProductos(config_file)
    Extraer.setup_driver()

    try:
        Extraer.buscar_extraer()
    finally:
        Extraer.close_driver()

    Extraer.save_to_excel(file_path)


if __name__ == "__main__":
    main()