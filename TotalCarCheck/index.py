from .connections import TotalCarCheck as TotalCarCheckAPI
from Utils.utils import flatten_dict
from Utils.logging import logger

def get_total_car_check(vrm, vin):
    try:
        tcc_api = TotalCarCheckAPI(vrm, vin)
        tcc_data = tcc_api.check_vin()
        
        if not tcc_data:
            return None

        # Flatten the tcc_data dictionary
        flattened_data = flatten_dict(tcc_data)
    
        return flattened_data
    except Exception as e:
        logger.write(str(e), is_exception=True)
        return None

__all__ = ['get_total_car_check']
