# api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date

from core.models import Currency, CurrencyExchangeRate
from core.services import get_exchange_rate_data, convert_amount
from .serializers import (
    CurrencySerializer, 
    CurrencyExchangeRateSerializer,
    CurrencyRatesListSerializer,
    ConvertAmountSerializer
)

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class CurrencyExchangeRateViewSet(viewsets.ModelViewSet):
    queryset = CurrencyExchangeRate.objects.all()
    serializer_class = CurrencyExchangeRateSerializer
    
    @action(detail=False, methods=['post'])
    def rates_list(self, request):
        serializer = CurrencyRatesListSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        source_currency = data['source_currency']
        date_from = data['date_from']
        date_to = data['date_to']
        
        try:
            source = Currency.objects.get(code=source_currency)
            rates = CurrencyExchangeRate.objects.filter(
                source_currency=source,
                valuation_date__gte=date_from,
                valuation_date__lte=date_to
            ).order_by('valuation_date', 'exchanged_currency')
            
            if not rates.exists():
                return Response(
                    {"error": "No rates found for the specified period"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            currencies = Currency.objects.exclude(code=source_currency)
            result = []
            
            for rate_date in rates.values_list('valuation_date', flat=True).distinct():
                date_rates = {}
                date_rates['date'] = rate_date
                
                for currency in currencies:
                    rate = rates.filter(
                        exchanged_currency=currency,
                        valuation_date=rate_date
                    ).first()
                    
                    if rate:
                        date_rates[currency.code] = float(rate.rate_value)
                    
                result.append(date_rates)
            
            return Response(result)
            
        except Currency.DoesNotExist:
            return Response(
                {"error": f"Currency {source_currency} not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def convert(self, request):
        serializer = ConvertAmountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        result = convert_amount(
            source_currency=data['source_currency'],
            amount=data['amount'],
            exchanged_currency=data['exchanged_currency'],
            valuation_date=data.get('valuation_date')
        )
        
        if not result.get('success'):
            return Response(
                {"error": result.get('error', 'Conversion failed')}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(result)