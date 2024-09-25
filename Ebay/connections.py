import requests
import os
from dotenv import load_dotenv
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta

class EbayBrowseApiConsumer:
    BASE_URL = "https://api.ebay.com/buy/browse/v2"
    
    def __init__(self):
        # Load environment variables and set up authentication headers
        load_dotenv()
        self.oauth_token = os.getenv('EBAY_OAUTH_TOKEN')
        self.headers = {
            "Authorization": f"Bearer {self.oauth_token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY-GB",
            "Content-Type": "application/json"
        }

    def search_items(self, 
                     keywords: str, 
                     category_id: Optional[str] = None,
                     min_price: Optional[float] = None,
                     max_price: Optional[float] = None,
                     condition: Optional[List[str]] = None,
                     year_start: Optional[int] = None,
                     year_end: Optional[int] = None,
                     limit: int = 50) -> Dict:
        # Construct URL and parameters for item search
        url = f"{self.BASE_URL}/item_summary/search"
        params = {
            "q": keywords,
            "limit": limit
        }
        
        # Add optional parameters and filters
        if category_id:
            params["category_ids"] = category_id
        
        filters = []
        if min_price:
            filters.append(f"price:[{min_price}..]")
        if max_price:
            filters.append(f"price:[..{max_price}]")
        if condition:
            filters.append(f"conditions:{{{','.join(condition)}}}")
        if year_start and year_end:
            filters.append(f"vehicleYear:[{year_start}..{year_end}]")
        if filters:
            params["filter"] = ",".join(filters)

        # Make API request and handle response
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

    def get_item_details(self, item_id: str) -> Dict:
        url = f"{self.BASE_URL}/item/{item_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

    def get_price_range(self, results: Dict) -> Tuple[Optional[float], Optional[float]]:
        prices = [float(item['price']['value']) for item in results.get('itemSummaries', [])]
        if prices:
            return min(prices), max(prices)
        return None, None

    def get_past_listings(self, 
                          make: str, 
                          model: str, 
                          year_start: int, 
                          year_end: int, 
                          days: int, 
                          limit: int = 100) -> List[Dict]:
        # Calculate date range for past listings
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=days)
        
        keywords = f"{make} {model}"
        
        results = self.search_items(
            keywords=keywords,
            category_id="9801",  # Cars, Motorcycles & Vehicles category
            year_start=year_start,
            year_end=year_end,
            limit=limit,
            condition=["USED", "PRE_OWNED"]
        )
        
        # Filter results based on end date
        filtered_results = [
            item for item in results.get('itemSummaries', [])
            if 'itemEndDate' in item and start_date <= datetime.fromisoformat(item['itemEndDate'][:-1]) <= end_date
        ]
        
        return filtered_results

    def get_active_listings(self, 
                            make: str, 
                            model: str, 
                            year_start: int, 
                            year_end: int, 
                            limit: int = 100) -> List[Dict]:
        keywords = f"{make} {model}"
        
        results = self.search_items(
            keywords=keywords,
            category_id="9801",  # Cars, Motorcycles & Vehicles category
            year_start=year_start,
            year_end=year_end,
            limit=limit,
            condition=["USED", "PRE_OWNED"]
        )
        
        return results.get('itemSummaries', [])

def print_item_summary(item: Dict):
    print(f"Title: {item['title']}")
    print(f"Price: £{item['price']['value']}")
    print(f"Condition: {item.get('condition', 'N/A')}")
    print(f"Item ID: {item['itemId']}")
    print("---")

def print_item_details(item: Dict):
    print(f"Title: {item['title']}")
    print(f"Price: £{item['price']['value']}")
    print(f"Condition: {item.get('condition', 'N/A')}")
    print(f"Location: {item['itemLocation'].get('city', 'N/A')}, {item['itemLocation'].get('country', 'N/A')}")
    print(f"Seller: {item['seller']['username']}")
    print(f"Item ID: {item['itemId']}")
    print("---")

def search_vehicles(api: EbayBrowseApiConsumer, make: str, model: str, year: str, limit: int = 10) -> List[Dict]:
    search_query = f"{make} {model}"
    year_start = int(year)
    year_end = int(year)
    results = api.search_items(keywords=search_query, category_id="9801", year_start=year_start, year_end=year_end, limit=limit, condition=["USED", "PRE_OWNED"])
    return results.get('itemSummaries', [])

def search_parts(api: EbayBrowseApiConsumer, make: str, model: str, year: str, part: str, limit: int = 10) -> List[Dict]:
    search_query = f"{make} {model} {part}"
    year_start = int(year)
    year_end = int(year)
    results = api.search_items(keywords=search_query, category_id="9884", year_start=year_start, year_end=year_end, limit=limit, condition=["USED", "PRE_OWNED"])
    return results.get('itemSummaries', [])

def main(make: str, model: str, year: str, part: str):
    ebay_api = EbayBrowseApiConsumer()

    # Vehicle search
    print(f"\nSearching for {year} {make} {model}...")
    vehicles = search_vehicles(ebay_api, make, model, year)

    if vehicles:
        print(f"\nFound {len(vehicles)} vehicles:")
        for vehicle in vehicles:
            print_item_summary(vehicle)

        lowest_price, highest_price = ebay_api.get_price_range({"itemSummaries": vehicles})
        if lowest_price and highest_price:
            print(f"\nPrice Range for {year} {make} {model}:")
            print(f"Lowest Price: £{lowest_price:.2f}")
            print(f"Highest Price: £{highest_price:.2f}")

        # Get details for the first vehicle
        first_vehicle_details = ebay_api.get_item_details(vehicles[0]['itemId'])
        print("\nDetails of the first vehicle:")
        print_item_details(first_vehicle_details)
    else:
        print(f"No vehicles found for {year} {make} {model}")

    # Parts search
    print(f"\nSearching for {part} for {year} {make} {model}...")
    parts = search_parts(ebay_api, make, model, year, part)

    if parts:
        print(f"\nFound {len(parts)} {part}s:")
        for part_item in parts:
            print_item_summary(part_item)

        lowest_price, highest_price = ebay_api.get_price_range({"itemSummaries": parts})
        if lowest_price and highest_price:
            print(f"\nPrice Range for {part}s:")
            print(f"Lowest Price: £{lowest_price:.2f}")
            print(f"Highest Price: £{highest_price:.2f}")

        # Get details for the first part
        first_part_details = ebay_api.get_item_details(parts[0]['itemId'])
        print(f"\nDetails of the first {part}:")
        print_item_details(first_part_details)
    else:
        print(f"No {part}s found for {year} {make} {model}")

    # Example usage of new methods
    print("\nTesting new methods:")
    
    # Past listings
    year_int = int(year)
    past_listings = ebay_api.get_past_listings(make, model, year_int-1, year_int+1, 30)
    print(f"\nFound {len(past_listings)} past listings:")
    for listing in past_listings[:5]:  # Print first 5 for brevity
        print_item_summary(listing)

    # Active listings
    active_listings = ebay_api.get_active_listings(make, model, year_int-1, year_int+1)
    print(f"\nFound {len(active_listings)} active listings:")
    for listing in active_listings[:5]:  # Print first 5 for brevity
        print_item_summary(listing)

if __name__ == "__main__":
    # Test data
    test_make = "Volkswagen"
    test_model = "Toureg"
    test_year = "2006"
    test_part = "set of rims"

    main(test_make, test_model, test_year, test_part)