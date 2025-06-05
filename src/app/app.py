import streamlit as st
import pandas as pd
import joblib
import os
import requests
from io import BytesIO
import pyodbc
import altair as alt
from streamlit_folium import st_folium
import folium
from auth import register_user, login_user   
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_prediction_email(to_email, subject, body, smtp_server, smtp_port, smtp_user, smtp_pass):
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())

# ---- ENVIRONMENT VARIABLES ----
model_url = os.getenv("BLOB_MODEL_URL")
city_map_url = os.getenv("BLOB_CITY_MAPPING_URL")
sql_conn_str = os.getenv("SQL_CONNECTION_STRING")
locations_csv_url  = os.getenv("BLOB_LOCATIONS_CSV_URL")
properties_csv_url = os.getenv("BLOB_PROPERTIES_CSV_URL")

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="🏡 RealValuator",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed",)


# ---- LANGUAGE SWITCH AND TRANSLATIONS ----
st.sidebar.markdown("### 🌐 Language / Język")
lang = st.sidebar.radio("", options=["PL", "EN"], index=0, horizontal=True)

T = {
    "PL": {
        "tabs": ["🏡 Kalkulator", "📋 Moje wyceny", "📈 Statystyki miast", "🗺️ Mapa"],
        "form_title": "Wprowadź szczegóły nieruchomości, by uzyskać wycenę",
        "address": "📍 Adres (opcjonalnie)",
        "address_help": "Możesz podać ulicę, ale tylko miasto wpływa na wycenę.",
        "city": "🌆 Miasto",
        "city_help": "Wybierz miasto nieruchomości.",
        "year": "🏗️ Rok budowy",
        "year_help": "Rok oddania budynku.",
        "floor": "⬆️ Piętro",
        "floor_help": "Na którym piętrze jest mieszkanie?",
        "rooms": "🛏️ Liczba pokoi",
        "rooms_help": "Podaj tylko pokoje mieszkalne (nie kuchnia/łazienka).",
        "area": "📐 Powierzchnia (m²)",
        "area_help": "Użytkowa powierzchnia mieszkania.",
        "predict": "🔮 Oblicz cenę",
        "spinner": "Obliczamy wycenę...",
        "est_price": "💰 Szacowana cena",
        "est_price_m2": "💸 Cena za m²",
        "data_res": "📋 Twoje dane i wyniki",
        "avg_price": "Średnia cena w {city}",
        "download": "📁 Pobierz wyniki jako CSV",
        "saved_sql": "🔄 Dane zapisane do Azure SQL ✅",
        "stat_tab_header": "📊 Średnie ceny w wybranych miastach",
        "ranking_city": "🏆 Ranking miast",
        "ranking_district": "🏆 Ranking dzielnic",
        "city_dist": "📈 Rozkład cen wg miasta",
        "district_dist": "📊 Rozkład cen wg dzielnicy",
        "map": "🗺️ Interaktywna mapa nieruchomości",
        "footer": "Autorzy: Michał Binda, Hubert Jaczyński, Aleksandra Kłos • v1.0  \n📧 Kontakt: realvaluator@gmail.com",
        "note": "Dodaj notatkę do predykcji:",
        "your_note": "Twoja notatka:",
        "anomaly": "⚠️ Możliwe anomalie lub sugestie:",
        "area_warn": "Powierzchnia musi być większa od 0, aby policzyć cenę za m².",
        "no_data_city": "Brak danych dla wybranego miasta.",
        "no_data_district": "Brak danych dla wybranej dzielnicy.",
        "no_districts": "Brak danych o dzielnicach dla tego miasta.",
        "login_tab": "Logowanie",
        "register_tab": "Rejestracja",
        "login": "Logowanie",
        "register": "Rejestracja",
        "username": "Nazwa użytkownika",
        "username_new": "Nowa nazwa użytkownika",
        "password": "Hasło",
        "password_new": "Nowe hasło",
        "email": "E-mail",
        "login_btn": "Zaloguj się",
        "register_btn": "Zarejestruj się",
        "login_success": "Zalogowano pomyślnie! Odświeżanie...",
        "register_success": "Rejestracja udana! Teraz możesz się zalogować.",
        "logout": "Wyloguj się",
        "logged_in_as": "👤 Zalogowano jako",
        "send_email": "Wyślij wynik na maila",
        "email_sent": "Wynik został wysłany na maila!",
        "email_fail": "Nie udało się wysłać maila: {err}",
        "enter_email": "Podaj swój adres email do otrzymania wyniku:",
        "no_history": "Brak zapisanych wycen.",
        "history_error": "Nie udało się pobrać historii: {err}",
    },
    "EN": {
        "tabs": ["🏡 Calculator", "📋 My predictions", "📈 Cities statistics", "🗺️ Map"],
        "form_title": "Enter your property details below to get an instant price estimate",
        "address": "📍 Address (optional)",
        "address_help": "You can type the street name. Only city affects prediction.",
        "city": "🌆 City",
        "city_help": "Choose the city where your property is located.",
        "year": "🏗️ Year of construction",
        "year_help": "Year the building was finished.",
        "floor": "⬆️ Floor number",
        "floor_help": "Which floor is the apartment on?",
        "rooms": "🛏️ Number of rooms",
        "rooms_help": "Living rooms and bedrooms only (not kitchen/bathroom).",
        "area": "📐 Living area (m²)",
        "area_help": "Usable floor area in m².",
        "predict": "🔮 Calculate price",
        "spinner": "Calculating the valuation...",
        "est_price": "💰 Estimated price",
        "est_price_m2": "💸 Estimated price per m²",
        "data_res": "📋 Your data and results",
        "avg_price": "Average in {city}",
        "download": "📁 Download results as CSV",
        "saved_sql": "🔄 Data saved to Azure SQL ✅",
        "stat_tab_header": "📊 Average prices for chosen cities",
        "ranking_city": "🏆 City ranking",
        "ranking_district": "🏆 District ranking",
        "city_dist": "📈 Price distribution by city",
        "district_dist": "📊 Price distribution by district",
        "map": "🗺️ Interactive property map",
        "footer": "Created by Michał Binda, Hubert Jaczyński, Aleksandra Kłos • v1.0  \n📧 Contact with us: realvaluator@gmail.com",
        "note": "Add a note for this prediction:",
        "your_note": "Your note:",
        "anomaly": "⚠️ Possible anomalies or suggestions:",
        "area_warn": "Area must be greater than 0 to calculate price per m².",
        "no_data_city": "No data for selected city.",
        "no_data_district": "No data for selected district.",
        "no_districts": "No district data found for this city.",
        "login_tab": "Login",
        "register_tab": "Register",
        "login": "Login",
        "register": "Register",
        "username": "Username",
        "username_new": "New username",
        "password": "Password",
        "password_new": "New password",
        "email": "E-mail",
        "login_btn": "Log in",
        "register_btn": "Register",
        "login_success": "Login successful! Refreshing...",
        "register_success": "Registration successful! You can now log in.",
        "logout": "Log out",
        "logged_in_as": "👤 Logged in as",
        "send_email": "Send result to email",
        "email_sent": "The result has been sent to your email!",
        "email_fail": "Failed to send email: {err}",
        "enter_email": "Enter your email to receive the result:",
        "no_history": "No saved predictions.",
        "history_error": "Could not fetch your history: {err}",
    }
}[lang]

# ---- SESSION STATE ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "prediction_note" not in st.session_state:
    st.session_state.prediction_note = ""

# ---- LOGIN/REGISTER UI ----
if not st.session_state.logged_in:
    st.title("🔐 RealValuator")
    tab_log, tab_reg = st.tabs([T["login_tab"], T["register_tab"]])
    with tab_log:
        st.subheader(T["login"])
        username = st.text_input(T["username"], key="login_user")
        password = st.text_input(T["password"], type="password", key="login_pw")
        if st.button(T["login_btn"]):
            ok, msg = login_user(username, password, sql_conn_str)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(T["login_success"])
                st.rerun()
            else:
                st.error(msg)
    with tab_reg:
        st.subheader(T["register"])
        new_username = st.text_input(T["username_new"], key="reg_user")
        new_email = st.text_input(T["email"], key="reg_email")
        new_password = st.text_input(T["password_new"], type="password", key="reg_pw")
        if st.button(T["register_btn"]):
            ok, msg = register_user(new_username, new_email, new_password, sql_conn_str)
            if ok:
                st.success(T["register_success"])
            else:
                st.error(msg)
    st.stop()
else:
    st.sidebar.write(f"{T['logged_in_as']} **{st.session_state.username}**")
    if st.sidebar.button(T["logout"]):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.prediction_note = ""
        st.success("You have been logged out successfully.")
        st.rerun()
        

# ---- STYLING ----
st.markdown("""
<style>
body { background-color: #1b1c1e; }
.stButton>button {
    background-color: #2e7bcf;
    color: white;
    border-radius: 10px;
    font-size: 18px;
    padding: 10px 24px;
    margin-top: 8px;
}
.stTextInput>div>input, .stNumberInput input {
    border-radius: 10px;
    padding: 8px;
}
.stDataFrame, .stTable {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px #0002;
}
div[data-testid="stForm"] {
    background: #22272b;
    padding: 18px 20px 8px 20px;
    border-radius: 18px;
    box-shadow: 0 2px 12px #0003;
}
</style>
""", unsafe_allow_html=True)


# ---- CACHED LOADING FUNCTIONS ----
@st.cache_resource(show_spinner=False)
def load_joblib_from_url(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return joblib.load(BytesIO(resp.content))

@st.cache_data(show_spinner=False)
def load_csv_from_url(url, encoding=None):
    return pd.read_csv(url, encoding=encoding)

@st.cache_data(show_spinner=False)
def calculate_stats(properties_df, cities):
    avg_prices = {}
    avg_prices_m2 = {}
    for city in cities:
        mask = properties_df["city"].astype(str).str.lower().str.contains(city[:4].lower())
        filtered = properties_df[mask]
        if not filtered.empty:
            avg_prices[city] = round(filtered["price"].mean(), 2)
            avg_prices_m2[city] = round((filtered["price"] / filtered["sq"]).mean(), 2)
        else:
            avg_prices[city] = None
            avg_prices_m2[city] = None
    return avg_prices, avg_prices_m2

# ---- LOAD RESOURCES ----
model        = load_joblib_from_url(model_url)
city_mapping = load_joblib_from_url(city_map_url)
city_encoder = {v:k for k,v in city_mapping.items()}

locations_df = load_csv_from_url(locations_csv_url) if locations_csv_url else None
properties_df = load_csv_from_url(properties_csv_url, encoding="cp1250") if properties_csv_url else None

cities = ["Poznań", "Warszawa", "Kraków"]
if properties_df is not None:
    avg_prices, avg_prices_m2 = calculate_stats(properties_df, cities)
else:
    avg_prices, avg_prices_m2 = {}, {}

# ---- TABS ----
tab1, tab_history, tab2, tab3 = st.tabs(T["tabs"])


with tab1:
    st.title("🏡 RealValuator")
    st.markdown(f"#### {T['form_title']}")

    if locations_df is not None and "Title" in locations_df.columns:
        city_list = locations_df["Title"].tolist()
    else:
        city_list = list(city_encoder.keys())

    # ---- PREDICTION FORM ----
    with st.form("predict_form"):
        col1, col2 = st.columns(2)
        with col1:
            address = st.text_input(
                T["address"],
                value=st.session_state.get("address", ""),
                help=T["address_help"]
            )
            city = st.selectbox(
                T["city"],
                options=city_list,
                index=city_list.index(st.session_state.get("city", city_list[0])) if st.session_state.get("city") in city_list else 0,
                help=T["city_help"]
            )
            year = st.number_input(
                T["year"], min_value=1900, max_value=2025, value=st.session_state.get("year", 2000), help=T["year_help"]
            )
        with col2:
            floor = st.number_input(
                T["floor"], min_value=0, max_value=50, value=st.session_state.get("floor", 0), help=T["floor_help"]
            )
            rooms = st.number_input(
                T["rooms"], min_value=1, max_value=10, value=st.session_state.get("rooms", 3), help=T["rooms_help"]
            )
            sq = st.number_input(
                T["area"], min_value=10.0, max_value=500.0, value=st.session_state.get("sq", 50.0), step=0.5, help=T["area_help"]
            )

        note = st.text_area(T["note"], key="prediction_note", value=st.session_state.get("prediction_note", ""))
        submitted = st.form_submit_button(T["predict"])

    # ---- LOGIKA PREDYKCJI + ZAPIS DO SQL ----
    if submitted:
        code = None
        if city in city_encoder.values():
            code = list(city_encoder.keys())[list(city_encoder.values()).index(city)]
        elif city in city_encoder:
            code = city_encoder[city]
        else:
            st.error(f"Selected city '{city}' not found in city mapping.")
            st.stop()

        X = pd.DataFrame([{
            "city_code": code,
            "floor": floor,
            "rooms": rooms,
            "sq": sq,
            "year": year}])

        with st.spinner(T["spinner"]):
            prediction = model.predict(X)[0]
        price_per_m2 = prediction / sq if sq > 0 else None

        # Save prediction data for the email form
        st.session_state.prediction_data = {
            "address": address,
            "city": city,
            "floor": floor,
            "rooms": rooms,
            "sq": sq,
            "year": year,
            "prediction": prediction,
            "price_per_m2": price_per_m2,
            "note": note,}

        st.session_state.address = address
        st.session_state.city = city
        st.session_state.year = year
        st.session_state.floor = floor
        st.session_state.rooms = rooms
        st.session_state.sq = sq

        st.success(f"{T['est_price']}: {prediction:,.0f} PLN", icon="✅")

        if price_per_m2:
            st.info(f"{T['est_price_m2']}: {price_per_m2:,.0f} PLN")
        else:
            st.warning(T["area_warn"])

        avg_price = avg_prices.get(city, None)
        if avg_price:
            compare_df = pd.DataFrame({
                "Category": [T['est_price'], T['avg_price'].format(city=city)],
                "Price": [prediction, avg_price],
            })
            bar_colors = ["#7400cc", "#58a6ff"]
            chart = alt.Chart(compare_df).mark_bar(size=60).encode(
                x=alt.X("Category", sort=None, title=None),
                y=alt.Y("Price", title="Price (PLN)"),
                color=alt.Color("Category", scale=alt.Scale(range=bar_colors), legend=None),
                tooltip=["Category", "Price"]
            ).properties(width=400, height=320)
            text = chart.mark_text(
                align='center', baseline='bottom', dy=-5, color='white', fontSize=16
            ).encode(
                text='Price:Q'
            )
            st.altair_chart(chart + text, use_container_width=True)

        # Hints/anomalies
        hints = []
        if sq / rooms < 10:
            hints.append("Very low area per room - is the number of rooms correct?" if lang == "EN" else "Bardzo mała powierzchnia na pokój - czy liczba pokoi jest poprawna?")
        if floor > 30:
            hints.append("Floor number is unusually high - check if this is not a typo." if lang == "EN" else "Wysokie piętro - sprawdź, czy nie ma literówki.")
        if year < 1920 or year > 2025:
            hints.append("Year of construction is unusual - double-check the value." if lang == "EN" else "Rok budowy jest nietypowy – sprawdź wartość.")
        if rooms > 10:
            hints.append("Number of rooms is rarely this high for one property." if lang == "EN" else "Liczba pokoi jest bardzo wysoka.")
        if hints:
            st.warning(T["anomaly"] + "\n- " + "\n- ".join(hints))

        # Results table
        st.markdown(f"#### {T['data_res']}")
        st.dataframe(pd.DataFrame([{
            T["city"]: city,
            T["floor"]: floor,
            T["rooms"]: rooms,
            T["area"]: sq,
            T["year"]: year,
            T["est_price"]: round(prediction,2),
            T["est_price_m2"]: round(price_per_m2, 2) if sq > 0 else "-"
        }]), hide_index=True, use_container_width=True)

        # Note
        if note:
            st.info(f"{T['your_note']} {note}")

        # Download CSV
        result = {
            "address": address,
            "city": city,
            "floor": floor,
            "rooms": rooms,
            "sq": sq,
            "year": year,
            "price": float(prediction)
        }
        df_out = pd.DataFrame([result])
        csv = df_out.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=T["download"],
            data=csv,
            file_name="realvaluatord_prediction.csv",
            mime="text/csv",
        )

        try:
            conn = pyodbc.connect(sql_conn_str)
            cursor = conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (
                    SELECT * FROM sys.tables WHERE name='predictions')
                CREATE TABLE predictions (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    username NVARCHAR(100),
                    address NVARCHAR(MAX),
                    city NVARCHAR(100),
                    floor INT,
                    rooms INT,
                    sq FLOAT,
                    year INT,
                    price FLOAT
                )
            """)
            cursor.execute("""
                INSERT INTO predictions (username, address, city, floor, rooms, sq, year, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, st.session_state.username, address, city, floor, rooms, sq, year, float(prediction))
            conn.commit()
            conn.close()
            st.info(T["saved_sql"])
        except Exception as err:
            st.warning(f"⚠️ Could not save to SQL: {err}")

    # ---- EMAIL FORM ----
    if "prediction_data" in st.session_state and st.session_state.prediction_data.get("prediction") is not None:
        with st.form("send_email_form"):
            user_email = st.text_input(T["enter_email"], value=st.session_state.get("email", ""), key="email_input")
            send_email = st.form_submit_button(T["send_email"])
        if send_email:
            data = st.session_state.prediction_data
            if user_email:
                SMTP_SERVER = "smtp.gmail.com"
                SMTP_PORT = 465
                SMTP_USER = os.getenv("SMTP_USER") or "realvaluator@gmail.com"
                SMTP_PASS = os.getenv("SMTP_PASS") or "YOUR_SMTP_PASSWORD" " 
                mail_subject = "Your property valuation from RealValuator"
                mail_body = f"""
Hello {st.session_state.username},

Your property valuation from RealValuator:

Adress: {data['address']}
City: {data['city']}
Floor: {data['floor']}
Number of rooms: {data['rooms']}
Area: {data['sq']} m²
Year of construction: {data['year']}

Estimated price: {data['prediction']:,.0f} PLN
Estimated price per m²: {data['price_per_m2']:,.0f} PLN

Note: {data['note'] if data['note'] else '-'}

Thanks for using RealValuator!  

With best regards,
RealValuator team - Michał Binda, Hubert Jaczyński, Aleksandra Kłos
"""
                try:
                    send_prediction_email(
                        user_email, mail_subject, mail_body,
                        SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS
                    )
                    st.session_state.email = user_email
                    st.success(T["email_sent"])
                except Exception as e:
                    st.error(T["email_fail"].format(err=e))
            else:
                st.warning("Please enter your email address to receive the valuation.")

def get_user_predictions(username, sql_conn_str):
    conn = pyodbc.connect(sql_conn_str)
    df = pd.read_sql("SELECT * FROM predictions WHERE username = ?", conn, params=[username])
    conn.close()
    return df

def delete_single_prediction(row_id, sql_conn_str):
    conn = pyodbc.connect(sql_conn_str)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE id = ?", row_id)
    conn.commit()
    conn.close()

def delete_user_predictions(username, sql_conn_str):
    conn = pyodbc.connect(sql_conn_str)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE username = ?", username)
    conn.commit()
    conn.close()


with tab_history:
    st.header("📋 Moje wyceny" if lang=="PL" else "📋 My predictions")
    if st.session_state.username:
        try:
            user_df = get_user_predictions(st.session_state.username, sql_conn_str)
            if not user_df.empty:

                for idx, row in user_df.iterrows():
                    cols = st.columns((6,1))
                    with cols[0]:
                        st.write(
                            f"{T['city']}: **{row['city']}** | "
                            f"{T['floor']}: {row['floor']} | "
                            f"{T['rooms']}: {row['rooms']} | "
                            f"{T['area']}: {row['sq']} | "
                            f"{T['year']}: {row['year']} | "
                            f"{T['est_price']}: {row['price']:,.0f} PLN"
                        )
                    with cols[1]:
                        del_btn = st.button("🗑️", key=f"del_{row['id']}", help="Usuń wycenę" if lang=="PL" else "Delete this entry")
                        if del_btn:
                            delete_single_prediction(row['id'], sql_conn_str)
                            st.success("Wycena usunięta!" if lang=="PL" else "Prediction deleted!")
                            st.rerun()
     
                delete_text = "🗑️ Usuń całą historię" if lang == "PL" else "🗑️ Delete all history"
                if st.button(delete_text, type="primary"):
                    delete_user_predictions(st.session_state.username, sql_conn_str)
                    st.success("Historia usunięta!" if lang=="PL" else "History deleted!")
                    st.rerun()
            else:
                st.info(T["no_history"])
        except Exception as e:
            st.error(T["history_error"].format(err=e))


with tab2:
    st.header(T["stat_tab_header"])
    if properties_df is not None:
        col11, col12 = st.columns(2)
        with col11:
            df_avg_price = pd.DataFrame.from_dict(avg_prices, orient="index", columns=["Average apartment price (PLN)"])
            chart1 = alt.Chart(df_avg_price.reset_index()).mark_bar(size=60, color="#23a3ff").encode(
                x=alt.X("index:N", title=T["city"]),
                y=alt.Y("Average apartment price (PLN)", title="Price (PLN)"),
                tooltip=["index", "Average apartment price (PLN)"]
            ).properties(width=360, height=270)
            st.altair_chart(chart1, use_container_width=True)
        with col12:
            df_avg_price_m2 = pd.DataFrame.from_dict(avg_prices_m2, orient="index", columns=["Average price for m² (PLN)"])
            chart2 = alt.Chart(df_avg_price_m2.reset_index()).mark_bar(size=60, color="#d6b27a").encode(
                x=alt.X("index:N", title=T["city"]),
                y=alt.Y("Average price for m² (PLN)", title="Price per m² (PLN)"),
                tooltip=["index", "Average price for m² (PLN)"]
            ).properties(width=360, height=270)
            st.altair_chart(chart2, use_container_width=True)

        # --- CITY RANKING ---
        st.subheader(T["ranking_city"])
        rank_df = df_avg_price.join(df_avg_price_m2)
        st.markdown("#### By average apartment price (PLN):")
        st.dataframe(
            rank_df[["Average apartment price (PLN)"]]
            .sort_values("Average apartment price (PLN)", ascending=False),
            use_container_width=True,
            hide_index=False
        )
        st.markdown("#### By average price per m² (PLN):")
        st.dataframe(
            rank_df[["Average price for m² (PLN)"]]
            .sort_values("Average price for m² (PLN)", ascending=False),
            use_container_width=True,
            hide_index=False
        )

        # --- DISTRICT RANKING ---
        st.markdown("---")
        st.subheader(T["ranking_district"])
        city_choice = st.selectbox(T["city"], cities, key="city_district_rank")
        mask = properties_df["city"].astype(str).str.lower().str.contains(city_choice[:4].lower())
        districts = (
            properties_df[mask]["address"].astype(str).str.split(" ", expand=True)[0]
            .str.capitalize()
        )
        exclude = {
            "Kraków": ["małopolskie", "kraków"],
            "Poznań": ["wielkopolskie", "poznań"],
            "Warszawa": ["mazowieckie", "warszawa"],}

        allowed = [
            d for d in districts.unique()
            if d not in [x.capitalize() for x in exclude.get(city_choice, [])] and len(d) > 2]

        ranking = []
        for district in allowed:
            dmask = properties_df["address"].astype(str).str.contains(district, case=False, na=False)
            prices = properties_df[mask & dmask & properties_df["price"].notnull()]
            if len(prices) > 5:
                mean_price = prices["price"].mean()
                mean_m2 = (prices["price"]/prices["sq"]).mean()
                ranking.append({"District": district, "Average price (PLN)": round(mean_price,0), "Average price per m² (PLN)": round(mean_m2,0)})
        rank_distr_df = pd.DataFrame(ranking).sort_values("Average price (PLN)", ascending=False)
        st.dataframe(rank_distr_df, use_container_width=True, hide_index=True)

        # --- PRICE DISTRIBUTION BY CITY ---
        st.markdown("---")
        st.subheader(T["city_dist"])
        city_hist_choice = st.selectbox(T["city"], cities, key="city_hist")
        city_mask = properties_df["city"].astype(str).str.lower().str.contains(city_hist_choice[:4].lower())
        city_prices = properties_df[city_mask & properties_df["price"].notnull()]["price"]
        if not city_prices.empty:
            hist_city = alt.Chart(pd.DataFrame({"price": city_prices})).mark_bar(
                color="#1fa1d6", opacity=0.7
            ).encode(
                alt.X("price", bin=alt.Bin(maxbins=40), title="Price [PLN]"),
                y="count()",
                tooltip=[alt.Tooltip("count()", title="Number of offers")]
            ).properties(width=450, height=270, title=f"Price distribution in {city_hist_choice}")
            st.altair_chart(hist_city, use_container_width=True)
        else:
            st.info("No data for selected city.")

        # --- PRICE DISTRIBUTION BY DISTRICT ---
        st.markdown("---")
        st.subheader(T["district_dist"])
        districts_for_hist = [
            d for d in districts.unique()
            if d not in [x.capitalize() for x in exclude.get(city_choice, [])] and len(d) > 2]

        if districts_for_hist:
            district_hist = st.selectbox("Choose district", sorted(districts_for_hist), key="district_hist")
            district_mask = properties_df["address"].astype(str).str.contains(district_hist, case=False, na=False)
            prices_district = properties_df[mask & district_mask & properties_df["price"].notnull()]["price"]
            if not prices_district.empty:
                hist_dist = alt.Chart(pd.DataFrame({"price": prices_district})).mark_bar(
                    color="#b067db", opacity=0.75
                ).encode(
                    alt.X("price", bin=alt.Bin(maxbins=30), title="Price [PLN]"),
                    y="count()",
                    tooltip=[alt.Tooltip("count()", title="Number of offers")]
                ).properties(width=450, height=270, title=f"Price distribution in {district_hist} ({city_choice})")
                st.altair_chart(hist_dist, use_container_width=True)
            else:
                st.info("No data for selected district.")
        else:
            st.info("No district data found for this city.")

with tab3:
    st.header(T["map"])
    if properties_df is not None:

        # --- FILTERS ---
        st.markdown("#### 🎚️ " + ("Filtry" if lang == "PL" else "Filters"))
        cities_on_map = properties_df["city"].dropna().unique()
        selected_city = st.selectbox(
            "🌆 Miasto" if lang == "PL" else "🌆 City",
            options=sorted(cities_on_map), 
            index=0, key="map_city_filter")


        filtered_df = properties_df[properties_df["city"] == selected_city]


        min_price, max_price = int(filtered_df["price"].min()), int(filtered_df["price"].max())
        price_range = st.slider(
            "💰 Zakres ceny (PLN)" if lang == "PL" else "💰 Price range (PLN)",
            min_value=min_price, max_value=max_price,
            value=(min_price, max_price), step=10000, key="map_price_filter")

        min_area, max_area = int(filtered_df["sq"].min()), int(filtered_df["sq"].max())
        area_range = st.slider(
            "📐 Zakres powierzchni (m²)" if lang == "PL" else "📐 Area range (m²)",
            min_value=min_area, max_value=max_area,
            value=(min_area, max_area), step=1, key="map_area_filter")

        min_rooms, max_rooms = int(filtered_df["rooms"].min()), int(filtered_df["rooms"].max())
        rooms_range = st.slider(
            "🛏️ Zakres liczby pokoi" if lang == "PL" else "🛏️ Number of rooms",
            min_value=min_rooms, max_value=max_rooms,
            value=(min_rooms, max_rooms), step=1, key="map_rooms_filter")

        map_sample = filtered_df[
            (filtered_df["price"] >= price_range[0]) & (filtered_df["price"] <= price_range[1]) &
            (filtered_df["sq"] >= area_range[0]) & (filtered_df["sq"] <= area_range[1]) &
            (filtered_df["rooms"] >= rooms_range[0]) & (filtered_df["rooms"] <= rooms_range[1])
        ].dropna(subset=["latitude", "longitude", "price", "city", "sq", "address"])


        map_sample = map_sample.sample(min(1000, len(map_sample)), random_state=42) if len(map_sample) > 0 else map_sample

        # --- MAP ---
        if not map_sample.empty:
            m = folium.Map(location=[map_sample["latitude"].mean(), map_sample["longitude"].mean()], zoom_start=12)
            for _, row in map_sample.iterrows():
                popup_content = f"""
                <b>{'Miasto' if lang == 'PL' else 'City'}:</b> {row['city']}<br>
                <b>{'Cena' if lang == 'PL' else 'Price'}:</b> {row['price']:,.0f} PLN<br>
                <b>{'Powierzchnia' if lang == 'PL' else 'Area'}:</b> {row['sq']} m²<br>
                <b>{'Pokoje' if lang == 'PL' else 'Rooms'}:</b> {row['rooms']}<br>
                <b>{'Adres' if lang == 'PL' else 'Address'}:</b> {row['address']}
                """
                folium.CircleMarker(
                    location=[row["latitude"], row["longitude"]],
                    radius=5,
                    popup=popup_content,
                    color="blue",
                    fill=True,
                    fill_opacity=0.5,
                ).add_to(m)
            st_folium(m, width=720, height=470)
            st.info(
                f"Znaleziono ofert: {len(map_sample)}" if lang=="PL" else f"Listings found: {len(map_sample)}"
            )
        else:
            st.warning(
                "Brak wyników dla wybranych filtrów." if lang=="PL" else "No listings for selected filters.")


st.markdown("---")
st.caption(T["footer"])
