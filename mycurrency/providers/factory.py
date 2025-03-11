from django.conf import settings
from typing import List, Dict, Any

from .adapter import (
    ProviderAdapter,
    CurrencyBeaconAdapter,
    ExchangeRateAdapter,
    OpenExchangeRatesAdapter,
    MockAdapter
)

class ProviderFactory:
    @staticmethod
    def get_provider(provider_name: str) -> ProviderAdapter:
        """Get provider adapter by name"""
        providers = {
            'currencybeacon': CurrencyBeaconAdapter,
            'exchangerate': ExchangeRateAdapter,
            'openexchangerates': OpenExchangeRatesAdapter,
            'mock': MockAdapter,
        }
        
        if provider_name not in providers:
            raise ValueError(f"Provider {provider_name} not supported")
        
        return providers[provider_name]()
    
    @staticmethod
    def get_active_providers() -> List[Dict[str, Any]]:
        """Get all active providers sorted by priority"""
        providers_config = settings.CURRENCY_PROVIDERS
        active_providers = []
        
        for name, config in providers_config.items():
            if config.get('active', False):
                active_providers.append({
                    'name': name,
                    'priority': config.get('priority', 999)
                })
        
        return sorted(active_providers, key=lambda x: x['priority'])