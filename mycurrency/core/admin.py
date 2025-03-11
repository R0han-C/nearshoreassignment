from django.contrib import admin
from django import forms
from django.shortcuts import render
from django.urls import path
from django.http import JsonResponse
from decimal import Decimal
from datetime import date

from .models import Currency, CurrencyExchangeRate
from .services import convert_amount
from .tasks import load_historical_exchange_rates
class CurrencyAdminSite(admin.AdminSite):
    site_header = "MyCurrency Administration"
    site_title = "MyCurrency Admin Portal"
    index_title = "Welcome to MyCurrency Portal"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('currency-converter/', self.admin_view(self.currency_converter_view), name='currency-converter'),
            path('load-historical-data/', self.admin_view(self.load_historical_data_view), name='load-historical-data'),
            path('api/convert/', self.admin_view(self.convert_api), name='convert-api'),
        ]
        return custom_urls + urls
    
    def currency_converter_view(self, request):
        form = CurrencyConverterForm()
        context = {
            'form': form,
            'title': 'Currency Converter',
            **self.each_context(request),
        }
        return render(request, 'admin/currency_converter.html', context)

    def load_historical_data_view(self, request):
        if request.method == 'POST':
            form = HistoricalDataForm(request.POST)
            if form.is_valid():
                days_back = form.cleaned_data['days_back']
                source_currencies = [c.code for c in form.cleaned_data['source_currencies']]
                target_currencies = [c.code for c in form.cleaned_data['target_currencies']]
                
                task = load_historical_exchange_rates.delay(
                    days_back=days_back,
                    source_currencies=source_currencies,
                    target_currencies=target_currencies
                )
                
                context = {
                    'title': 'Historical Data Loading',
                    'task_id': task.id,
                    'message': f'Task scheduled to load {days_back} days of historical data',
                    **self.each_context(request),
                }
                return render(request, 'admin/historical_data_result.html', context)
        else:
            initial_currencies = Currency.objects.filter(code__in=['EUR', 'USD', 'GBP', 'CHF'])
            form = HistoricalDataForm(initial={
                'source_currencies': initial_currencies,
                'target_currencies': initial_currencies
            })
        
        context = {
            'form': form,
            'title': 'Load Historical Exchange Rate Data',
            **self.each_context(request),
        }
        return render(request, 'admin/load_historical_data.html', context)

    def convert_api(self, request):
        if request.method == 'POST':
            source_id = request.POST.get('source_currency')
            amount_str = request.POST.get('amount')
            target_ids = request.POST.getlist('target_currencies')
            
            try:
                source_currency = Currency.objects.get(id=source_id)
                amount = Decimal(amount_str)
                target_currencies = Currency.objects.filter(id__in=target_ids)
                
                results = []
                for target in target_currencies:
                    if target.id == source_currency.id:
                        results.append({
                            'currency': target.code,
                            'amount': float(amount),
                            'success': True
                        })
                        continue
                    
                    result = convert_amount(
                        source_currency=source_currency.code,
                        amount=amount,
                        exchanged_currency=target.code
                    )
                    
                    if result.get('success'):
                        results.append({
                            'currency': target.code,
                            'amount': float(result['converted_amount']),
                            'rate': float(result['rate']),
                            'success': True
                        })
                    else:
                        results.append({
                            'currency': target.code,
                            'error': result.get('error', 'Conversion failed'),
                            'success': False
                        })
                
                return JsonResponse({'results': results})
            
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        
        return JsonResponse({'error': 'Method not allowed'}, status=405)

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol')
    search_fields = ('code', 'name')

class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('source_currency', 'exchanged_currency', 'valuation_date', 'rate_value', 'provider')
    list_filter = ('source_currency', 'exchanged_currency', 'valuation_date', 'provider')
    search_fields = ('source_currency__code', 'exchanged_currency__code')
    date_hierarchy = 'valuation_date'

class CurrencyConverterForm(forms.Form):
    source_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(),
        label="Source Currency"
    )
    amount = forms.DecimalField(
        min_value=0.01,
        max_digits=18,
        decimal_places=2,
        label="Amount"
    )
    target_currencies = forms.ModelMultipleChoiceField(
        queryset=Currency.objects.all(),
        label="Target Currencies"
    )

class HistoricalDataForm(forms.Form):
    days_back = forms.IntegerField(
        min_value=1,
        max_value=365,
        initial=30,
        label="Days Back"
    )
    source_currencies = forms.ModelMultipleChoiceField(
        queryset=Currency.objects.all(),
        label="Source Currencies"
    )
    target_currencies = forms.ModelMultipleChoiceField(
        queryset=Currency.objects.all(),
        label="Target Currencies"
    )

admin_site = CurrencyAdminSite(name='mycurrency_admin')

admin_site.register(Currency, CurrencyAdmin)
admin_site.register(CurrencyExchangeRate, CurrencyExchangeRateAdmin)

admin.site.register(Currency, CurrencyAdmin)
admin.site.register(CurrencyExchangeRate, CurrencyExchangeRateAdmin)