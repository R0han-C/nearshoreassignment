FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY redis_start.sh .
RUN chmod +x redis_start.sh
COPY . .
RUN apt-get update && apt-get install -y redis-server && apt-get clean
EXPOSE 5000
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=mycurrency.settings
CMD ["sh", "-c", "./redis_start.sh && python mycurrency/manage.py runserver 0.0.0.0:8000"]