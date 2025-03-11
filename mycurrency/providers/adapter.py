from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
import random
import requests
from django.conf import settings
from typing import Dict, Any, Optional

class ProviderAdapter(ABC):
    @abstractmethod
    def get_exchange_rate(self, source_currency: str, exchanged_currency: str, valuation_date: date) -> Dict[str, Any]:
        """Get exchange rate data from provider."""
        pass

class CurrencyBeaconAdapter(ProviderAdapter):
    def __init__(self):
        self.api_key = settings.CURRENCY_PROVIDERS['currencybeacon']['api_key']
        # Import later from env
        self.base_url = "https://api.currencybeacon.com/v1"
        
    def get_exchange_rate(self, source_currency: str, exchanged_currency: str, valuation_date: date) -> Dict[str, Any]:
        url = f"{self.base_url}/historical"
        params = {
            'api_key': self.api_key,
            'base': source_currency,
            'symbols': exchanged_currency,
            'date': valuation_date.strftime('%Y-%m-%d')
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'rates' in data and exchanged_currency in data['rates']:
                return {
                    'source_currency': source_currency,
                    'exchanged_currency': exchanged_currency,
                    'valuation_date': valuation_date,
                    'rate_value': Decimal(str(data['rates'][exchanged_currency])),
                    'provider': 'currencybeacon',
                    'success': True
                }
            return {'success': False, 'error': 'Invalid response from CurrencyBeacon'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class ExchangeRateAdapter(ProviderAdapter):
    def __init__(self):
        self.api_key = settings.CURRENCY_PROVIDERS['exchangerate']['api_key']
        # Import later from env
        self.base_url = "https://v6.exchangerate-api.com/v6"
        
    def get_exchange_rate(self, source_currency: str, exchanged_currency: str, valuation_date: date) -> Dict[str, Any]:
        url = f"{self.base_url}/{self.api_key}/pair/{source_currency}/{exchanged_currency}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get('result') == 'success' and 'conversion_rate' in data:
                return {
                    'source_currency': source_currency,
                    'exchanged_currency': exchanged_currency,
                    'valuation_date': valuation_date,
                    'rate_value': Decimal(str(data['conversion_rate'])),
                    'provider': 'exchangerate',
                    'success': True
                }
            return {'success': False, 'error': 'Invalid response from ExchangeRate API'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class OpenExchangeRatesAdapter(ProviderAdapter):
    def __init__(self):
        self.api_key = settings.CURRENCY_PROVIDERS['openexchangerates']['api_key']
        self.base_url = "https://openexchangerates.org/api"
        
    def get_exchange_rate(self, source_currency: str, exchanged_currency: str, valuation_date: date) -> Dict[str, Any]:
        url = f"{self.base_url}/historical/{valuation_date.strftime('%Y-%m-%d')}.json"
        params = {'app_id': self.api_key}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'rates' in data:
                if source_currency == 'USD':
                    rate = Decimal(str(data['rates'].get(exchanged_currency, 0)))
                elif exchanged_currency == 'USD':
                    source_rate = Decimal(str(data['rates'].get(source_currency, 0)))
                    rate = Decimal('1') / source_rate if source_rate else 0
                else:
                    source_rate = Decimal(str(data['rates'].get(source_currency, 0)))
                    target_rate = Decimal(str(data['rates'].get(exchanged_currency, 0)))
                    rate = target_rate / source_rate if source_rate else 0
                
                return {
                    'source_currency': source_currency,
                    'exchanged_currency': exchanged_currency,
                    'valuation_date': valuation_date,
                    'rate_value': rate,
                    'provider': 'openexchangerates',
                    'success': True
                }
            return {'success': False, 'error': 'Invalid response from OpenExchangeRates'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class MockAdapter(ProviderAdapter):
    def get_exchange_rate(self, source_currency: str, exchanged_currency: str, valuation_date: date) -> Dict[str, Any]:
        base_rates = {
            'EUR': Decimal('1.0'),
            'USD': Decimal('1.08'),
            'GBP': Decimal('0.85'),
            'CHF': Decimal('0.98'),
        }
        
        if source_currency not in base_rates or exchanged_currency not in base_rates:
            return {'success': False, 'error': 'Currency not supported by Mock provider'}
        
        source_rate = base_rates[source_currency]
        target_rate = base_rates[exchanged_currency]
        
        variability = Decimal(str(random.uniform(-0.02, 0.02)))
        rate = (target_rate / source_rate) * (1 + variability)
        
        return {
            'source_currency': source_currency,
            'exchanged_currency': exchanged_currency,
            'valuation_date': valuation_date,
            'rate_value': rate.quantize(Decimal('0.000001')),
            'provider': 'mock',
            'success': True
        }