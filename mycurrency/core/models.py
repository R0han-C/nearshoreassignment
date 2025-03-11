from django.db import models

class ProtectedModel(models.Model):
    class Meta:
        abstract = True

class Currency(ProtectedModel):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20, db_index=True)
    symbol = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.code} ({self.name})"
    
    class Meta:
        verbose_name_plural = "Currencies"

class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey(Currency, related_name='exchanges', on_delete=models.CASCADE)
    exchanged_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(db_index=True, decimal_places=6, max_digits=18)
    provider = models.CharField(max_length=50, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.source_currency.code}/{self.exchanged_currency.code}: {self.rate_value} ({self.valuation_date})"
    
    class Meta:
        unique_together = ('source_currency', 'exchanged_currency', 'valuation_date', 'provider')