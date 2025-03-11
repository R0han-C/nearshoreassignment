from django.core.management.base import BaseCommand
from core.models import Currency

class Command(BaseCommand):
    help = 'Seeds the database with initial currency data'

    def handle(self, *args, **options):
        currencies = [
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},
            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£'},
            {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'Fr'},
        ]
        
        for currency_data in currencies:
            Currency.objects.get_or_create(
                code=currency_data['code'],
                defaults={
                    'name': currency_data['name'],
                    'symbol': currency_data['symbol']
                }
            )
            
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(currencies)} currencies'))