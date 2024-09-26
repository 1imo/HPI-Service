from .connections import AutoTraderAPI
from Utils.utils import flatten_dict

def get_autotrader_listings(vehicle_data):
    # Initialize the AutoTrader API client
    autotrader_api = AutoTraderAPI()

    # Fetch market data from AutoTrader API using vehicle information
    market_data = autotrader_api.get_market_data(
        make=vehicle_data.vehicle_info.make,
        model=vehicle_data.vehicle_info.model,
        year=vehicle_data.vehicle_info.year
    )
    
    # Update vehicle_data with market information
    vehicle_data.market_data.estimated_value = market_data.get("estimated_value", 0.0)
    vehicle_data.market_data.price_range = (
        market_data.get("min_price", 0),
        market_data.get("max_price", 0)
    )
    vehicle_data.market_data.days_to_sell = market_data.get("average_days_to_sell", 0)
    vehicle_data.market_data.similar_listings = market_data.get("similar_listings_count", 0)

    # Convert vehicle_data to a dictionary and flatten it
    vehicle_dict = vehicle_data.__dict__
    flattened_data = flatten_dict(vehicle_dict)

    # Return the flattened data dictionary
    return flattened_data

# Specify which functions should be importable when using "from AutoTrader import *"
__all__ = ['get_autotrader_listings']