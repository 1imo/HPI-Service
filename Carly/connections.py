import json
import os
from curl_cffi import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='../.env')

class CarlyVehicleHistory:
    def __init__(self):
        self.base_url = "https://vin.mycarly.io"

    def get_vehicle_history(self, vrm):
        url = f"{self.base_url}/vehicle-history"
        params = {
            'vrm': vrm,
            'locale': 'en-GB',
            'application_type': 'production',
            'mixpanel_user_id': os.getenv('MIXPANEL_USER_ID')
        }
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en;q=0.9',
            'carly-user-country': 'GB',
            'carly-user-id': os.getenv('CARLY_USER_ID'),
            'carly-user-lang': 'en',
            'Connection': 'keep-alive',
            'Host': 'vin.mycarly.io',
            'Origin': 'https://www.mycarly.com',
            'Referer': 'https://www.mycarly.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': os.getenv('USER_AGENT')
        }
        response = requests.get(url, params=params, headers=headers)
        print("RESPONSE", response.json())
        return response.json()['data']['url']

    def extract_vehicle_info(self, url, vrm):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'vin.mycarly.io',
            'User-Agent': os.getenv('USER_AGENT')
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        def clean_text(text):
            if text:
                text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces, newlines, tabs with a single space
                return text.strip()
            return None

        def parse_equipment(section):
            equipment = {}
            for item in section.find_all('li', class_='icon-nut-screw'):
                key_value = item.text.split(':')
                if len(key_value) == 2:
                    key, value = key_value
                    key = clean_text(key)
                    value = clean_text(value)
                    # Convert numeric values to int or float
                    if value and value.replace('.', '').isdigit():
                        value = float(value)
                        if value.is_integer():
                            value = int(value)
                    equipment[key] = value
            return equipment

        # Extracting the required information
        vehicle_info = {
            'vrm': vrm,
            'vin': clean_text(soup.find('code', class_='d-flex').text) if soup.find('code', class_='d-flex') else None,
            'brandName': clean_text(soup.find('div', class_='d-flex flex-column flex-grow-1 align-items-center').find('span').text) if soup.find('div', class_='d-flex flex-column flex-grow-1 align-items-center') else None,
            'model': clean_text(soup.find_all('div', class_='d-flex flex-column flex-grow-1 align-items-center')[1].find('span').text) if len(soup.find_all('div', class_='d-flex flex-column flex-grow-1 align-items-center')) > 1 else None,   
            'damages': [],
            'theft': None,
            'fuelType': clean_text(soup.find('div', {'data-fuelType': True})['data-fuelType']) if soup.find('div', {'data-fuelType': True}) else None
        }

        # Handle damages
        damages_section = soup.find('section', id='damages')
        if damages_section:
            damages = clean_text(damages_section.text)
            if not damages.startswith("No Damages Registered"):
                vehicle_info['damages'] = [damages]

        # Handle theft
        theft_section = soup.find('section', id='theft')
        if theft_section:
            theft = clean_text(theft_section.find('span').text)
            if theft != "No entry":
                vehicle_info['theft'] = theft

        # Parse equipment sections and flatten the data
        equipment_sections = {
            'consumption': soup.find('div', id='consumption'),
            'dimensions': soup.find('div', id='dimensions'),
            'engine': soup.find('div', id='engine'),
            'general': soup.find('div', id='general'),
            'performance': soup.find('div', id='performance')
        }

        for section in equipment_sections.values():
            if section:
                vehicle_info.update(parse_equipment(section))

        return vehicle_info

if __name__ == "__main__":
    carly = CarlyVehicleHistory()
    # vrm = "YL55KXS"  # Change the VRM here
    vrm = "YL55KXS"  # Change the VRM here
    response_data = carly.get_vehicle_history(vrm)
    vehicle_info = carly.extract_vehicle_info(response_data, vrm)
    print(json.dumps(vehicle_info, indent=4))