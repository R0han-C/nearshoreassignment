# Nearshore Assignment - MyCurrency 💲

A Django-based web platform for currency exchange rate conversion, with multiple provider support via the Adapter Design Pattern.

## Overview

MyCurrency is a web platform that allows users to calculate currency exchange rates. It integrates with external providers like CurrencyBeacon for real exchange rates and includes a mock provider for testing. The platform provides a REST API and an admin interface for currency conversion and historical data management.

## Features

- Currency management (EUR, USD, GBP, CHF)
- Multiple exchange rate providers (CurrencyBeacon and Mock)
- Automatic provider fallback if one fails
- Database caching of exchange rates
- RESTful API for currency conversion
- Custom admin interface
- Asynchronous historical data loading

## Tech Stack

- Python 3.11
- Django 5.0.2
- Django REST Framework 3.14.0
- PostgreSQL (or SQLite for development)
- Celery 5.2.7 with Redis
- Docker

## Quick Setup with Docker

### Clone the repository:

```bash
git clone https://github.com/R0han-C/nearshoreassignment.git
cd mycurrency
```

### Create a `.env` file with your settings:

```
SECRET_KEY=your-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

CURRENCYBEACON_API_KEY=your-api-key
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Build and start the Docker containers:
#### see logs for docker to confirm it is running.

```bash
sudo docker run -it -p 8000:8000 nearshorechallenge
```

## Manual Setup

### Create a virtual environment and install dependencies:

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure database in `settings.py` or use environment variables

### Run migrations and seed data:

```bash
python manage.py migrate
python manage.py seed_currencies
```

### Start the development server:

```bash
python manage.py runserver
```

### Start Celery worker:

```bash
celery -A mycurrency worker -l INFO
```

## API Endpoints

### Get all currencies:

```
GET /api/currencies/
```

### Convert currency:

```
POST /api/rates/convert/
Payload: {"source_currency": "USD", "amount": 100, "exchanged_currency": "EUR"}
```

### Get historical rates:

```
POST /api/rates/rates_list/
Payload: {"source_currency": "USD", "date_from": "2023-03-01", "date_to": "2023-03-10"}
```

## Admin Interface URLs

- **Admin Dashboard:** [http://localhost:8000/admin/](http://localhost:8000/admin/)
- **Currency Converter:** [http://localhost:8000/admin/currency-converter/](http://localhost:8000/admin/currency-converter/)
- **Historical Data Loading:** [http://localhost:8000/admin/load-historical-data/](http://localhost:8000/admin/load-historical-data/)

## Project Structure

```
mycurrency/
├── api/                  # API app
├── core/                 # Core app with models and business logic
├── providers/            # Currency providers implementation
│   ├── adapters/         # Adapter pattern implementation
│   └── factory.py        # Provider factory
└── mycurrency/           # Project settings
```

## Implementation Notes

- Uses Adapter Pattern for currency providers
- Implements provider fallback mechanism for resilience
- Caches exchange rates in database for performance
- Uses Celery for asynchronous historical data loading
- Follows Django best practices for code organization

## Troubleshooting

- If Celery doesn't start, check Redis connection and broker URL
- For API connection issues, verify API keys in settings
- Ensure PostgreSQL is running if using it as database

## Future Improvements

- Add more currency providers
- Implement comprehensive test suite
- Add user authentication for API access
- Create a frontend interface for end users
