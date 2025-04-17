import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

DATA_PATH = 'src/data/properties.csv'

df = pd.read_csv(DATA_PATH, encoding='cp1250') # encoding for Polish characters
df = df.drop(['id', 'address', 'latitude', 'longitude', 'Unnamed: 0'], axis=1, errors='ignore')

df['city'] = df['city'].astype('category')
df['city_code'] = df['city'].cat.codes
city_mapping = dict(enumerate(df['city'].cat.categories))

X = df[['city_code', 'floor', 'rooms', 'sq', 'year']]
y = df['price']

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)
os.makedirs('src/model', exist_ok=True)
joblib.dump(model, 'src/model/model.pkl')
joblib.dump(city_mapping, 'src/model/city_mapping.pkl')

print("Model has been trained and saved to the src/model/ directory.")
