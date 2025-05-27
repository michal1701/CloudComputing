import azure.functions as func
import logging
import os
import json
import requests
import joblib
from io import BytesIO
import pandas as pd

def load_city_mapping():
    city_mapping_url = os.environ.get("BLOB_CITY_MAPPING_URL")
    if not city_mapping_url:
        raise ValueError("BLOB_CITY_MAPPING_URL not configured.")
    response = requests.get(city_mapping_url)
    if response.status_code != 200:
        raise Exception(f"Failed to load city mapping. Status code: {response.status_code}")
    mapping = joblib.load(BytesIO(response.content))
    city_encoder = {v: k for k, v in mapping.items()}
    return city_encoder

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Predict function triggered.")
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON provided.", status_code=400)
    
    city_name = req_body.get("city")
    floor = req_body.get("floor")
    rooms = req_body.get("rooms")
    sq = req_body.get("sq")
    year = req_body.get("year")

    if None in (city_name, floor, rooms, sq, year):
        return func.HttpResponse("Missing one or more required fields.", status_code=400)
    
    try:
        city_encoder = load_city_mapping()
    except Exception as e:
        logging.error(f"Error loading city mapping: {str(e)}")
        return func.HttpResponse("Error loading city mapping.", status_code=500)
    
    if city_name not in city_encoder:
        return func.HttpResponse("City not found in mapping.", status_code=400)
    
    city_code = city_encoder[city_name]
    
    blob_model_url = os.environ.get("BLOB_MODEL_URL")
    if not blob_model_url:
        return func.HttpResponse("BLOB_MODEL_URL not configured.", status_code=500)
    
    response = requests.get(blob_model_url)
    if response.status_code != 200:
        return func.HttpResponse(f"Failed to load model. Status code: {response.status_code}", status_code=500)
    
    try:
        model = joblib.load(BytesIO(response.content))
    except Exception as e:
        logging.error(f"Error loading model: {str(e)}")
        return func.HttpResponse("Error loading model.", status_code=500)
    
    try:
        input_df = pd.DataFrame([{
            'city_code': city_code,
            'floor': floor,
            'rooms': rooms,
            'sq': sq,
            'year': year
        }])
    except Exception as e:
        logging.error(f"Error preparing input data: {str(e)}")
        return func.HttpResponse("Error preparing input data.", status_code=500)
    
    try:
        prediction = model.predict(input_df)[0]
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        return func.HttpResponse(f"Prediction error: {str(e)}", status_code=500)
    
    result = {
        "estimated_value": prediction,
        "currency": "PLN"
    }
    return func.HttpResponse(json.dumps(result), mimetype="application/json", status_code=200)
