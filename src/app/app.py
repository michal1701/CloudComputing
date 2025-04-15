import os
import streamlit as st
import pandas as pd
import requests
import json
from dotenv import load_dotenv

load_dotenv()

FUNCTION_API_URL = os.environ.get("FUNCTION_API_URL")
if not FUNCTION_API_URL:
    st.error("FUNCTION_API_URL environment variable is not defined.")
    st.stop()

st.title("🏡 RealValuator - Real estate price prediction")
st.write("Insert data to get a predicted price of a property.")

with st.form(key='prediction_form'):
    address = st.text_input("Address (optional)")
    city = st.text_input("City")  
    floor = st.number_input("Floor", min_value=0, step=1)
    rooms = st.number_input("Number of rooms", min_value=1, step=1)
    sq = st.number_input("Area (m²)", min_value=1.0, step=0.5)
    year = st.number_input("Year of construction", min_value=1850, max_value=2025, step=1)
    submit = st.form_submit_button("Predict price")

if submit:
    input_data = {
        "city": city,
        "floor": floor,
        "rooms": rooms,
        "sq": sq,
        "year": year
    }
    st.info("Sending prediction request to API...")

    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(FUNCTION_API_URL, headers=headers, data=json.dumps(input_data))
        if response.status_code == 200:
            result = response.json()
            predicted_price = result.get("estimated_value")
            st.success(f"💰 Predicted price: {predicted_price:,.2f} zł")
        else:
            st.error(f"API error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error calling prediction API: {e}")
