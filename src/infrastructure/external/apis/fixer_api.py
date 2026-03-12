# Cliente real para API Fixer.io"""
import os
import requests
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FixerAPI:
    """Cliente para API Fixer.io com dados reais"""
    
    def __init__(self):
        self.api_key = os.getenv("FIXER_API_KEY")
        self.base_url = "http://data.fixer.io/api/latest"
        
        if not self.api_key:
            logger.warning("⚠️ FIXER_API_KEY não configurada. Usando dados simulados.")
    
    def get_latest_rates(self, symbols: List[str] = None) -> Optional[Dict]:
        """
        Busca taxas de câmbio reais da API Fixer.io
        """
        if not self.api_key:
            return self._get_mock_rates(symbols)
        
        try:
            params = {
                "access_key": self.api_key,
                "base": "EUR"  # Fixer usa EUR como base no plano gratuito
            }
            
            if symbols:
                params["symbols"] = ",".join(symbols)
            
            logger.info(f"📡 Consultando Fixer.io para moedas: {symbols}")
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if data.get("success"):
                rates = data["rates"]
                logger.info(f"✅ Dados recebidos: {list(rates.keys())}")
                
                # Converter para USD base se necessário
                if "USD" in rates:
                    usd_rate = rates["USD"]
                    rates_usd = {
                        currency: round(rate / usd_rate, 4)
                        for currency, rate in rates.items()
                    }
                    rates_usd["USD"] = 1.0
                    return {
                        "base": "USD",
                        "date": data["date"],
                        "rates": rates_usd,
                        "original_rates": rates,
                        "eur_usd": usd_rate
                    }
                
                return {
                    "base": "EUR",
                    "date": data["date"],
                    "rates": rates
                }
            else:
                error = data.get("error", {})
                logger.error(f"❌ Erro Fixer.io: {error}")
                return self._get_mock_rates(symbols)
                
        except Exception as e:
            logger.error(f"❌ Erro ao acessar Fixer.io: {e}")
            return self._get_mock_rates(symbols)
    
    def _get_mock_rates(self, symbols: List[str] = None) -> Dict:
        """Dados simulados para fallback"""
        logger.warning("⚠️ Usando dados simulados")
        
        mock_rates = {
            "USD": 1.0,
            "BRL": 5.25,
            "EUR": 0.92,
            "GBP": 0.79,
            "JPY": 151.50,
            "CNY": 7.15,
            "CAD": 1.35,
            "AUD": 1.52,
            "CHF": 0.89,
            "RUB": 92.50
        }
        
        if symbols:
            return {s: mock_rates.get(s, 1.0) for s in symbols}
        return mock_rates
    
    def get_historical_rates(self, date: str, symbols: List[str] = None) -> Optional[Dict]:
        """
        Busca taxas históricas (requer plano pago)
        """
        # Por enquanto, retorna dados simulados
        return self._get_mock_rates(symbols)