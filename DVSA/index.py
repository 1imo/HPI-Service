from .connections import MOTHistoryRetriever as DVSAAPI
from Models.vehicle import MOTTest
from datetime import datetime
import os
import json

def get_mot_history(vrm):
    dvsa_api = DVSAAPI()
    mot_history = dvsa_api.fetch_mot_history(vrm)

    return mot_history

__all__ = ['get_mot_history']