import requests
import json

healthy = {
    "age": 60.0, "sex": "M", "spo2": 95.0, "respiratory_rate": 18.0, 
    "temperature": 37.0, "heart_rate": 80.0,
    "altered_mentation": 0, "chest_pain": 0, "diabetes": 0, "systolic_bp": 120, "diastolic_bp": 80,
    "wbc": 7.5, "hemoglobin": 14.0, "platelet_count": 250, "sodium": 140, "potassium": 4.0, "creatinine": 0.9, "glucose": 100, "troponin": 0.01, "bnp": 50, "lactate": 1.2, "inr": 1.0
}

high_risk = {
    "age": 72.0, "sex": "F", "spo2": 88.0, "respiratory_rate": 28.0, 
    "temperature": 38.5, "heart_rate": 105.0,
    "altered_mentation": 1, "chest_pain": 1, "diabetes": 1, "systolic_bp": 90, "diastolic_bp": 60,
    "wbc": 15.5, "hemoglobin": 10.0, "platelet_count": 150, "sodium": 135, "potassium": 3.5, "creatinine": 1.5, "glucose": 180, "troponin": 0.1, "bnp": 200, "lactate": 3.5, "inr": 1.5
}

try:
    print("Healthy:")
    res1 = requests.post('http://localhost:8000/unified/predict', json=healthy)
    print(json.dumps(res1.json(), indent=2))
except Exception as e:
    print("Error:", e)

try:
    print("\nHigh Risk:")
    res2 = requests.post('http://localhost:8000/unified/predict', json=high_risk)
    print(json.dumps(res2.json(), indent=2))
except Exception as e:
    print("Error:", e)
