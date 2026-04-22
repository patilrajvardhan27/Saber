FROM python:3.11-slim

WORKDIR /app

COPY API's/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY BldgAuditToolSimple_v1/ ./BldgAuditToolSimple_v1/
COPY API's/main.py ./main.py

EXPOSE 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
