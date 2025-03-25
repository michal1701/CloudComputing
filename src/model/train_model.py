import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

# Ścieżka do danych
DATA_PATH = 'src/data/properties.csv'

# Wczytanie danych z odpowiednim kodowaniem (ważne dla polskich znaków)
df = pd.read_csv(DATA_PATH, encoding='cp1250')

# Usunięcie niepotrzebnych kolumn
df = df.drop(['id', 'address', 'latitude', 'longitude', 'Unnamed: 0'], axis=1, errors='ignore')

# Zakodowanie miasta jako liczby (Label Encoding)
df['city'] = df['city'].astype('category')
df['city_code'] = df['city'].cat.codes

# Zapamiętanie mapowania miasta (np. "Warszawa" → 0)
city_mapping = dict(enumerate(df['city'].cat.categories))

# Przygotowanie danych do treningu
X = df[['city_code', 'floor', 'rooms', 'sq', 'year']]
y = df['price']

# Trenowanie modelu Random Forest
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Upewnij się, że folder model/ istnieje
os.makedirs('src/model', exist_ok=True)

# Zapisanie modelu
joblib.dump(model, 'src/model/model.pkl')

# Zapisanie mapowania miast
joblib.dump(city_mapping, 'src/model/city_mapping.pkl')

print("✅ Model został wytrenowany i zapisany do src/model/")
