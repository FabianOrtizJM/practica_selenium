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
            for sub_action in action['actions']:
                if sub_action['action'] == 'find_elements_table_columns':
                    headers = [header.text for header in table.find_elements(By.TAG_NAME, sub_action['value'])]
                    self.data_store[sub_action['save_as']] = headers
                elif sub_action['action'] == 'get_element_text_list':
                    data = []
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    for row in rows[1:]:
                        cols = row.find_elements(By.TAG_NAME, sub_action['value'])
                        cols = [col.text for col in cols]
                        data.append(cols)
                    self.data_store[sub_action['save_as']] = data

        if 'output' in action:
            self.save_output(action['output'])

    def save_output(self, output_config):
        columns = output_config.get('columns')
        if isinstance(columns, str):
            columns = columns.split(', ')
        filename = output_config['filename']
        if self.extracted_data:
            self.save_to_excel(filename, columns)
            self.extracted_data = []
        elif 'headers' in self.data_store and 'rows' in self.data_store:
            self.save_table_to_excel(filename, self.data_store['headers'], self.data_store['rows'])
        else:
            print("No data to save en {filename}")

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
                print(f"Storing data: {data}")  # Depura los datos que se van a almacenar
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
                if 'action' in action:
                    self.execute_action(action)
                elif 'output' in action:
                    self.save_output(action['output'])
        finally:
            self.close_driver()

    def save_table_to_excel(self, filename, headers, data):
        print(f"Headers: {headers}")
        for i, row in enumerate(data):
            print(f"Row {i}: {row}")
        adjusted_data = []
        for row in data:
            if len(row) == len(headers):
                adjusted_data.append(row)
            else:
                adjusted_data.append(row + [''] * (len(headers) - len(row)))
        df = pd.DataFrame(adjusted_data, columns=headers)
        df.to_excel(filename, index=False)

    def save_to_excel(self, filename, columns):
        if isinstance(columns, str):
            columns = columns.split(', ')
        if self.extracted_data:
            print(f"Saving data {len(self.extracted_data)} records to {filename}")
            df = pd.DataFrame(self.extracted_data, columns=columns)
            print(f"Dataframe: {df}")
            df.to_excel(filename, index=False)


def main(config_file):
    scraper = ejemploselenium(config_file)
    scraper.run()


if __name__ == "__main__":
    config_file = 'utt.json'
    main(config_file)