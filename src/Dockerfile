FROM python:3.9-slim

WORKDIR /app

COPY requirement.txt /app

RUN pip install --no-cache-dir -r requirement.txt

COPY app /app/app
COPY model /app/model
COPY database /app/database
COPY functions/predict /app/functions

EXPOSE 8501

CMD ["streamlit", "run", "app/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.enableCORS=false"]