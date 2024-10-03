from .connections import MOTHistoryRetriever as DVSAAPI
from Models.vehicle import MOTTest
from datetime import datetime
import os
import json
from Utils.logging import logger

def get_mot_history(vrm):
    try:
        dvsa_api = DVSAAPI()
        mot_history = dvsa_api.fetch_mot_history(vrm)

        return mot_history
    except Exception as e:
        logger.write(str(e), is_exception=True)

__all__ = ['get_mot_history']