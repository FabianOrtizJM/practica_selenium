from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import json
import time


class ejemploselenium:
    def __init__(self, config_file):
        self.driver = None
        self.config = self.load_config(config_file)
        self.extracted_data = []
        self.data_store = {}

    @staticmethod
    def load_config(config_file):
        with open(config_file, 'r') as file:
            return json.load(file)

    def setup_driver(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def execute_action(self, action):
        if action['action'] == 'input':
            element = self.find_element_with_wait(action['by'], action['value'])
            element.clear()
            element.send_keys(action['input_value'])
            element.send_keys(Keys.RETURN)

        elif action['action'] == 'click':
            element = self.find_element_with_wait(action['by'], action['value'])
            element.click()

        elif action['action'] == 'scroll':
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        elif action['action'] == 'wait':
            time.sleep(action['wait'])

        elif action['action'] == 'find_elements':
            elements = self.find_elements_with_wait(action['by'], action['value'])
            for element in elements:
                for sub_action in action['actions']:
                    self.execute_sub_action(element, sub_action)

        elif action['action'] == 'find_element_table':
            table = self.find_element_with_wait(action['by'], action['value'])
            rows = table.find_elements(By.TAG_NAME, 'tr')

            headers = [header.text for header in
                       rows[0].find_elements(By.TAG_NAME, self.config['actions'][2]['actions'][0]['value'])]
            data = []
            for row in rows[1:]:
                cols = row.find_elements(By.TAG_NAME, self.config['actions'][2]['actions'][1]['value'])
                cols = [col.text for col in cols]
                data.append(cols)

            self.data_store['headers'] = headers
            self.data_store['data'] = data

    def execute_sub_action(self, element, sub_action):
        try:
            if sub_action['action'] == 'click':
                sub_element = self.find_element_with_wait(sub_action['by'], sub_action['value'], element)
                sub_element.click()

            elif sub_action['action'] == 'get_element_text':
                sub_elements = element.find_elements(getattr(By, sub_action['by']), sub_action['value'])
                texts = [sub_element.text for sub_element in sub_elements]
                combined_text = ' '.join(texts)
                self.data_store[sub_action['save_as']] = combined_text

            elif sub_action['action'] == 'store_data':
                data = {key: self.data_store.get(value.strip('{}'), '') for key, value in sub_action['data'].items()}
                self.extracted_data.append(data)
        finally:
            pass


    def find_element_with_wait(self, by, value, context=None, timeout=10):
        context = context or self.driver
        return WebDriverWait(context, timeout).until(
            EC.presence_of_element_located((getattr(By, by), value))
        )

    def find_elements_with_wait(self, by, value, context=None, timeout=10):
        context = context or self.driver
        return WebDriverWait(context, timeout).until(
            EC.presence_of_all_elements_located((getattr(By, by), value))
        )

    def run(self):
        self.setup_driver()
        try:
            self.driver.get(self.config['start_url'])
            for action in self.config['actions']:
                self.execute_action(action)

            if 'headers' in self.data_store and 'data' in self.data_store:
                self.save_table_to_excel(self.config['output']['filename'], self.data_store['headers'],
                                         self.data_store['data'])
            else:
                self.save_to_excel(self.config['output']['filename'], self.config['output']['columns'])

        finally:
            self.close_driver()

    def save_table_to_excel(self, filename, headers, data):
        df = pd.DataFrame(data, columns=headers)
        df.to_excel(filename, index=False)

    def save_to_excel(self, filename, columns):
        df = pd.DataFrame(self.extracted_data, columns=columns)
        df.to_excel(filename, index=False)


def main(config_file):
    scraper = ejemploselenium(config_file)
    scraper.run()


if __name__ == "__main__":
    config_file = 'wikipedia_poblacion_mexico.json'  # Cambia esto según el archivo JSON que quieras usar
    main(config_file)