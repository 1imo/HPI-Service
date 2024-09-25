from .connections import MOTHistoryRetriever as DVSAAPI
from Models.vehicle import MOTTest
from datetime import datetime
import os
import json

def get_mot_history(vehicle_data):
    dvsa_api = DVSAAPI()
    mot_history = dvsa_api.fetch_mot_history(vehicle_data.vehicle_info.registration)

    vehicle_data.mot_history = []
    
    # Check if mot_history is a list with at least one item
    if isinstance(mot_history, list) and len(mot_history) > 0:
        mot_tests = mot_history[0].get("motTests", [])
        
        for test in mot_tests:
            mot_test = MOTTest(
                date=datetime.strptime(test.get("completedDate", "")[:10], "%Y-%m-%d").date(),
                result=test.get("testResult", ""),
                mileage=int(test.get("odometerValue", 0)),
                expiry_date=datetime.strptime(test.get("expiryDate", "")[:10], "%Y-%m-%d").date() if test.get("expiryDate") else None,
                advisories=[defect["text"] for defect in test.get("defects", []) if defect.get("type") == "ADVISORY"],
                defects=[defect["text"] for defect in test.get("defects", []) if defect.get("type") != "ADVISORY"]
            )
            vehicle_data.mot_history.append(mot_test)

    return vehicle_data

__all__ = ['get_mot_history']