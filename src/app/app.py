import streamlit as st
import pandas as pd
import joblib
import sqlite3
import os

# model loading and city mapping
model = joblib.load('model/model.pkl')
city_mapping = joblib.load('model/city_mapping.pkl')

# reverse city mapping to = name --> code
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

    # save to a database
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect('database/predictions.db')
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            address TEXT,
            city TEXT,
            floor INTEGER,
            rooms INTEGER,
            sq REAL,
            year INTEGER,
            price REAL
        )
    """)
    cur.execute("""
        INSERT INTO predictions (address, city, floor, rooms, sq, year, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (address, city, floor, rooms, sq, year, float(predicted_price)))
    conn.commit()
    conn.close()

    st.info("Data has been saved to the database. ✅")