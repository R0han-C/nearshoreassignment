from datetime import date
from decimal import Decimal
from typing import Dict, Any, Optional, List
import logging

from providers.factory import ProviderFactory
from core.models import Currency, CurrencyExchangeRate

logger = logging.getLogger(__name__)

def get_exchange_rate_data(
    source_currency: str,
    exchanged_currency: str,
    valuation_date: date,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    db_rate = None
    if not provider:
        try:
            source = Currency.objects.get(code=source_currency)
            target = Currency.objects.get(code=exchanged_currency)
            db_rate = CurrencyExchangeRate.objects.filter(
                source_currency=source,
                exchanged_currency=target,
                valuation_date=valuation_date
            ).order_by('-created_at').first()
        except (Currency.DoesNotExist, CurrencyExchangeRate.DoesNotExist):
            pass
    
    if db_rate:
        return {
            'source_currency': source_currency,
            'exchanged_currency': exchanged_currency,
            'valuation_date': valuation_date,
            'rate_value': db_rate.rate_value,
            'provider': db_rate.provider,
            'success': True,
            'from_database': True
        }

    if provider:
        try:
            adapter = ProviderFactory.get_provider(provider)
            result = adapter.get_exchange_rate(source_currency, exchanged_currency, valuation_date)
            if result.get('success'):
                _save_exchange_rate(result)
                return result
        except Exception as e:
            logger.error(f"Error with provider {provider}: {str(e)}")
            return {'success': False, 'error': str(e)}

    providers = ProviderFactory.get_active_providers()
    
    for provider_config in providers:
        provider_name = provider_config['name']
        try:
            adapter = ProviderFactory.get_provider(provider_name)
            result = adapter.get_exchange_rate(source_currency, exchanged_currency, valuation_date)
            if result.get('success'):
                _save_exchange_rate(result)
                return result
        except Exception as e:
            logger.error(f"Error with provider {provider_name}: {str(e)}")
            continue
    
    return {'success': False, 'error': 'No provider could fetch the exchange rate'}

def _save_exchange_rate(data: Dict[str, Any]):
    if not data.get('success'):
        return
    
    try:
        source, _ = Currency.objects.get_or_create(
            code=data['source_currency'],
            defaults={'name': data['source_currency'], 'symbol': data['source_currency']}
        )
        target, _ = Currency.objects.get_or_create(
            code=data['exchanged_currency'],
            defaults={'name': data['exchanged_currency'], 'symbol': data['exchanged_currency']}
        )
        
        CurrencyExchangeRate.objects.update_or_create(
            source_currency=source,
            exchanged_currency=target,
            valuation_date=data['valuation_date'],
            provider=data['provider'],
            defaults={'rate_value': data['rate_value']}
        )
    except Exception as e:
        logger.error(f"Error saving exchange rate: {str(e)}")

def convert_amount(
    source_currency: str,
    amount: Decimal,
    exchanged_currency: str,
    valuation_date: Optional[date] = None
) -> Dict[str, Any]:
    if valuation_date is None:
        valuation_date = date.today()
    
    rate_data = get_exchange_rate_data(
        source_currency=source_currency,
        exchanged_currency=exchanged_currency,
        valuation_date=valuation_date
    )
    
    if not rate_data.get('success'):
        return rate_data
    
    converted_amount = amount * rate_data['rate_value']
    
    return {
        'source_currency': source_currency,
        'amount': amount,
        'exchanged_currency': exchanged_currency,
        'converted_amount': converted_amount.quantize(Decimal('0.01')),
        'rate': rate_data['rate_value'],
        'valuation_date': valuation_date,
        'provider': rate_data['provider'],
        'success': True
    }