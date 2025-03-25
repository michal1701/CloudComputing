import streamlit as st
import pandas as pd
import joblib
import sqlite3
import os

# Wczytaj model i mapowanie miast
model = joblib.load('src/model/model.pkl')
city_mapping = joblib.load('src/model/city_mapping.pkl')

# Odwróć mapowanie miast na: nazwa → kod
city_encoder = {v: k for k, v in city_mapping.items()}

# Tytuł aplikacji
st.title("🏡 Predykcja ceny nieruchomości")
st.write("Wprowadź dane, aby otrzymać prognozowaną cenę mieszkania.")

with st.form(key='prediction_form'):
    address = st.text_input("Adres (opcjonalny)")
    city = st.selectbox("Miasto", list(city_encoder.keys()))
    floor = st.number_input("Piętro", min_value=0, step=1)
    rooms = st.number_input("Liczba pokoi", min_value=1, step=1)
    sq = st.number_input("Metraż (m²)", min_value=1.0, step=0.5)
    year = st.number_input("Rok budowy", min_value=1800, max_value=2100, step=1)
    submit = st.form_submit_button("Oblicz cenę")

if submit:
    try:
        city_code = city_encoder[city]
    except KeyError:
        st.error("Nieznane miasto. Spróbuj inne.")
        st.stop()

    # Przygotowanie danych
    input_data = pd.DataFrame([{
        'city_code': city_code,
        'floor': floor,
        'rooms': rooms,
        'sq': sq,
        'year': year
    }])

    # Predykcja
    predicted_price = model.predict(input_data)[0]
    st.success(f"💰 Szacowana cena: {predicted_price:,.2f} zł")

    # Zapis do bazy danych
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

    st.info("Dane zostały zapisane w bazie danych. ✅")
