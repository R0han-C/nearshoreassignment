from rest_framework import serializers
from core.models import Currency, CurrencyExchangeRate
from datetime import date

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol']

class CurrencyExchangeRateSerializer(serializers.ModelSerializer):
    source_currency_code = serializers.CharField(source='source_currency.code', read_only=True)
    exchanged_currency_code = serializers.CharField(source='exchanged_currency.code', read_only=True)
    
    class Meta:
        model = CurrencyExchangeRate
        fields = [
            'id', 'source_currency', 'exchanged_currency', 
            'source_currency_code', 'exchanged_currency_code',
            'valuation_date', 'rate_value', 'provider'
        ]

class CurrencyRatesListSerializer(serializers.Serializer):
    source_currency = serializers.CharField(max_length=3)
    date_from = serializers.DateField()
    date_to = serializers.DateField()

class ConvertAmountSerializer(serializers.Serializer):
    source_currency = serializers.CharField(max_length=3)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    exchanged_currency = serializers.CharField(max_length=3)
    valuation_date = serializers.DateField(required=False, default=date.today)