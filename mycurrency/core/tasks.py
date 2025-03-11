from celery import shared_task
import logging
from datetime import date, timedelta
from core.services import get_exchange_rate_data
from core.models import Currency

logger = logging.getLogger(__name__)

@shared_task
def load_historical_exchange_rates(
    days_back: int = 30,
    source_currencies: list = None,
    target_currencies: list = None
):

    if not source_currencies:
        source_currencies = ['EUR', 'USD', 'GBP', 'CHF']
    
    if not target_currencies:
        target_currencies = ['EUR', 'USD', 'GBP', 'CHF']
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)
    
    for code in set(source_currencies + target_currencies):
        Currency.objects.get_or_create(
            code=code,
            defaults={'name': code, 'symbol': code}
        )
    
    current_date = start_date
    success_count = 0
    error_count = 0
    
    while current_date <= end_date:
        for source in source_currencies:
            for target in target_currencies:
                if source == target:
                    continue
                    
                try:
                    result = get_exchange_rate_data(
                        source_currency=source,
                        exchanged_currency=target,
                        valuation_date=current_date
                    )
                    
                    if result.get('success'):
                        success_count += 1
                    else:
                        error_count += 1
                        logger.error(f"Failed to get rate for {source}/{target} on {current_date}: {result.get('error')}")
                
                except Exception as e:
                    error_count += 1
                    logger.error(f"Exception getting rate for {source}/{target} on {current_date}: {str(e)}")
                
        current_date += timedelta(days=1)
    
    return {
        'success_count': success_count,
        'error_count': error_count,
        'days_processed': days_back,
        'source_currencies': source_currencies,
        'target_currencies': target_currencies
    }