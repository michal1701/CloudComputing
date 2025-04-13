import os
import streamlit as st
import pandas as pd
import joblib
import requests
from io import BytesIO
import pyodbc
from dotenv import load_dotenv

# environment variables 
DB_CONNECTION = os.environ.get("DB_CONNECTION")
BLOB_MODEL_URL = os.environ.get("BLOB_MODEL_URL")
BLOB_CITY_MAPPING_URL = os.environ.get("BLOB_CITY_MAPPING_URL")

if not DB_CONNECTION or not BLOB_MODEL_URL or not BLOB_CITY_MAPPING_URL:
    st.error("Environment variables are not defined.")
    st.stop()

st.info("Loading model from Azure Blob Storage...")


response_model = requests.get(BLOB_MODEL_URL)
if response_model.status_code == 200:
    model = joblib.load(BytesIO(response_model.content))
    st.success("Model loaded successfully.")
else:
    st.error(f"Failed to load model. Status code: {response_model.status_code}")
    st.stop()


response_mapping = requests.get(BLOB_CITY_MAPPING_URL)
if response_mapping.status_code == 200:
    mapping = joblib.load(BytesIO(response_mapping.content))
    st.success("City mapping loaded successfully.")
else:
    st.error(f"Failed to load mapping. Status code: {response_mapping.status_code}")
    st.stop()


city_encoder = {v: k for k, v in mapping.items()}

st.title("🏡 Real estate price prediction")
st.write("Inset data to get a predicted price of a property.")

with st.form(key='prediction_form'):
    address = st.text_input("Adress (optional)")
    city = st.selectbox("City", list(city_encoder.keys()))
    floor = st.number_input("Floor", min_value=0, step=1)
    rooms = st.number_input("Number of rooms", min_value=1, step=1)
    sq = st.number_input("Area (m²)", min_value=1.0, step=0.5)
    year = st.number_input("Year of construction", min_value=1850, max_value=2025, step=1)
    submit = st.form_submit_button("Oblicz cenę")

if submit:
    try:
        city_code = city_encoder[city]
    except KeyError:
        st.error("Undefined city. Try selecting a different one.")
        st.stop()

    input_data = pd.DataFrame([{
        'city_code': city_code,
        'floor': floor,
        'rooms': rooms,
        'sq': sq,
        'year': year
    }])

    try:

        predicted_price = model.predict(input_data)[0]
    except Exception as e:
        st.error(f"Prediction error: {e}")
        st.stop()
    st.success(f"💰 Predicted price: {predicted_price:,.2f} zł")

    try:
        conn = pyodbc.connect(DB_CONNECTION)
        curr = conn.cursor()

        create_table_query = """
        IF NOT EXISTS (
        SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'predictions')
        BEGIN
            CREATE TABLE predictions (
                id INT IDENTITY(1,1) PRIMARY KEY,
                address NVARCHAR(255),
                city NVARCHAR(255),
                floor INT,
                rooms INT,
                sq FLOAT,
                year INT,
                predicted_price FLOAT,
                prediction_timestamp DATETIME DEFAULT GETDATE()
            )
        END
        """
        curr.execute(create_table_query)
        conn.commit()
        insert_query = """ INSERT INTO predictions (address, city, floor, rooms, sq, year, predicted_price) 
        VALUES (?, ?, ?, ?, ?, ?, ?) """
        curr.execute(insert_query, (address, city, floor, rooms, sq, year, predicted_price))
        conn.commit()
        st.info("Prediction saved to the database. ✅")
    except Exception as db_error:
        st.error(f"Error while saving data to the database: {db_error}")
    finally:
        try:
            conn.close()
        except Exception:
            pass