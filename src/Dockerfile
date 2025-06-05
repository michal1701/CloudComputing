FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    gnupg2 \
    apt-transport-https \
    ca-certificates

RUN apt-get purge -y unixodbc-dev unixodbc odbcinst1debian2 odbcinst libodbc1 || true

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirement.txt /app 

RUN pip install --no-cache-dir -r requirement.txt

COPY . /app/
COPY model /app/model
COPY database /app/database
COPY functions/predict /app/functions

EXPOSE 8501

CMD ["streamlit", "run", "app/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.enableCORS=false"]
