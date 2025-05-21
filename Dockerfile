FROM python:3.10.13-slim

WORKDIR /app

COPY requirements.txt .
COPY packages.txt .

RUN apt-get update && \
    apt-get install -y $(cat packages.txt) && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"] 