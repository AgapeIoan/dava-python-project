# Folosim imaginea oficiala pentru Python 3.12
FROM python:3.12-slim

# Setam directorul de lucru in container
WORKDIR /app

# Copiem fisierul cu dependinte mai intai pentru a beneficia de caching-ul Docker
COPY ./requirements.txt /app/requirements.txt

# Instalam dependintele
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Install sqlite3
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copiem tot codul sursa al aplicatiei
COPY ./app /app/app

# Expunem portul pe care va rula aplicatia
EXPOSE 8000

# Comanda care ruleaza la pornirea containerului
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]