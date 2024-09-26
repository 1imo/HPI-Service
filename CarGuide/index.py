from .connections import CarLookup
from datetime import datetime, timezone
from Utils.utils import flatten_dict

def get_car_details(vrm):
    car_lookup = CarLookup(vrm)
    car_details = car_lookup.get_car_details()
    
    vehicle_data = flatten_dict(car_details)

    return vehicle_data

# Make sure to export the function
__all__ = ['get_car_details']
