FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5432

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5432"]
