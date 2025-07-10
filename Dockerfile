FROM python:3.11-slim-buster

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install dependencies and clean up in single layer
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip/* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app

EXPOSE 8080

CMD ["python3", "app.py"]