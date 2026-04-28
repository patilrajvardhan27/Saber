FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .

EXPOSE 8080

# The folder is named "API's" — quote it carefully
CMD ["sh", "-c", "cd \"API's\" && exec uvicorn main:app --host 0.0.0.0 --port 8080"]
