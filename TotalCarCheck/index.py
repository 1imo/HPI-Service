from .connections import TotalCarCheck as TotalCarCheckAPI
from Utils.utils import flatten_dict

def get_total_car_check(vrm, vin):
    tcc_api = TotalCarCheckAPI(vrm, vin)
    tcc_data = tcc_api.check_vin()

    if tcc_data is None:
        return {}
    
    # Flatten the tcc_data dictionary
    flattened_data = flatten_dict(tcc_data)
    

    return flattened_data

__all__ = ['get_total_car_check']
