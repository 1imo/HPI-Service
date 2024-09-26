import json
from curl_cffi import requests

class CarLookup:
    BASE_URL = "https://ya6349wsii.execute-api.eu-west-2.amazonaws.com/prod/lookup"

    def __init__(self, vrm):
        self.vrm = vrm

    def get_car_details(self):
        try:
            url = f"{self.BASE_URL}?vrm={self.vrm}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = json.loads(response.text)
                # Remove MOT data from the response
                data.pop('motData', None)
                return data
            else:
                return {"error": f"Failed to fetch data. Status code: {response.status_code}"}
        except Exception as e:
            return {"error": f"Network error: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON parsing error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

if __name__ == "__main__":
    # Test with a sample VRM
    test_vrm = "YL55KXS"
    car_lookup = CarLookup(test_vrm)
    result = car_lookup.get_car_details()
    print(json.dumps(result, indent=2))