import streamlit as st
import pandas as pd
import joblib
import os
import requests
from io import BytesIO
import pyodbc

# model loading and city mapping
def load_joblib_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return joblib.load(BytesIO(response.content))

model_url = os.getenv("BLOB_MODEL_URL")
city_mapping_url = os.getenv("BLOB_CITY_MAPPING_URL")

if not model_url or not city_mapping_url:
    st.error("Blob URLs are not set in environment variables.")
    st.stop()

model = load_joblib_from_url(model_url)
city_mapping = load_joblib_from_url(city_mapping_url)
city_encoder = {v: k for k, v in city_mapping.items()}

st.title("🏡 RealValuator - Real estate price prediction")
st.write("Insert data to obtain the predicted price of a property.")

with st.form(key='prediction_form'):
    address = st.text_input("Address (optional)")
    city = st.selectbox("City", list(city_encoder.keys()))
    floor = st.number_input("Floor", min_value=0, step=1)
    rooms = st.number_input("Number of rooms", min_value=1, step=1)
    sq = st.number_input("Area (m²)", min_value=1.0, step=0.5)
    year = st.number_input("Year of construction", min_value=1800, max_value=2100, step=1)
    submit = st.form_submit_button("Calculate the price")

if submit:
    try:
        city_code = city_encoder[city]
    except KeyError:
        st.error("Unknown city. Try inserting a different one.")
        st.stop()

    input_data = pd.DataFrame([{
        'city_code': city_code,
        'floor': floor,
        'rooms': rooms,
        'sq': sq,
        'year': year
    }])

    # prediction
    predicted_price = model.predict(input_data)[0]
    st.success(f"💰 Predicted price: {predicted_price:,.2f} zł")

    # --- SAVE TO AZURE SQL ---
    sql_conn_str = os.getenv("SQL_CONNECTION_STRING")
    if not sql_conn_str:
        st.error("SQL_CONNECTION_STRING not set in environment variables.")
        st.stop()

    def ensure_table_exists(cursor):
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='predictions' and xtype='U')
            CREATE TABLE predictions (
                address NVARCHAR(MAX),
                city NVARCHAR(100),
                floor INT,
                rooms INT,
                sq FLOAT,
                year INT,
                price FLOAT
            )
        """)

    try:
        conn = pyodbc.connect(sql_conn_str)
        cur = conn.cursor()
        ensure_table_exists(cur)
        cur.execute("""
            INSERT INTO predictions (address, city, floor, rooms, sq, year, price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (address, city, floor, rooms, sq, year, float(predicted_price)))
        conn.commit()
        conn.close()
        st.info("Data has been saved to the Azure SQL database. ✅")
    except Exception as e:
        st.error(f"Failed to save to Azure SQL DB: {e}")
