"""APIs alternativas para taxas de câmbio"""
import requests
import logging
from typing import Optional, Dict, List
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class ExchangeAlternatives:
    """Cliente para APIs alternativas de câmbio"""
    
    def __init__(self):
        self.apis = [
            {
                "name": "ExchangeRate-API (free tier)",
                "url": "https://api.exchangerate-api.com/v4/latest/USD",
                "parser": self._parse_exchangerate_api,
                "requires_key": False
            },
            {
                "name": "Frankfurter (free)",
                "url": "https://api.frankfurter.app/latest",
                "parser": self._parse_frankfurter,
                "requires_key": False
            },
            {
                "name": "CurrencyAPI (free tier)",
                "url": "https://api.currencyapi.com/v3/latest",
                "parser": self._parse_currencyapi,
                "requires_key": True,
                "key_env": "CURRENCY_API_KEY"
            }
        ]
    
    def get_rates(self, symbols: List[str] = None) -> Optional[Dict]:
        """Tenta obter taxas de APIs alternativas"""
        
        for api in self.apis:
            try:
                logger.info(f"📡 Tentando API alternativa: {api['name']}")
                
                # Verificar se precisa de chave
                if api.get("requires_key"):
                    api_key = os.getenv(api.get("key_env"))
                    if not api_key:
                        logger.warning(f"⚠️ {api['name']} requer chave não configurada")
                        continue
                    url = f"{api['url']}?apikey={api_key}"
                else:
                    url = api["url"]
                
                response = requests.get(url, timeout=8)
                
                if response.status_code == 200:
                    data = response.json()
                    rates = api["parser"](data, symbols)
                    
                    if rates:
                        logger.info(f"✅ Dados obtidos via {api['name']}")
                        return {
                            "base": "USD",
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "rates": rates,
                            "source": api["name"]
                        }
                else:
                    logger.warning(f"⚠️ {api['name']} retornou status {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ {api['name']} falhou: {e}")
                continue
        
        logger.error("❌ Todas as APIs alternativas falharam")
        return None
    
    def _parse_exchangerate_api(self, data: dict, symbols: List[str] = None) -> Dict:
        """Parser para ExchangeRate-API"""
        if "rates" in data:
            rates = data["rates"]
            if symbols:
                return {s: rates.get(s, 1.0) for s in symbols if s in rates}
            return rates
        return None
    
    def _parse_frankfurter(self, data: dict, symbols: List[str] = None) -> Dict:
        """Parser para Frankfurter (dados do ECB)"""
        if "rates" in data:
            rates = data["rates"]
            # Frankfurter usa EUR como base
            if "USD" in rates:
                usd_rate = rates["USD"]
                rates_usd = {currency: round(rate / usd_rate, 4) for currency, rate in rates.items()}
                rates_usd["USD"] = 1.0
                
                if symbols:
                    return {s: rates_usd.get(s, 1.0) for s in symbols if s in rates_usd}
                return rates_usd
        return None
    
    def _parse_currencyapi(self, data: dict, symbols: List[str] = None) -> Dict:
        """Parser para CurrencyAPI"""
        if "data" in data:
            rates = {k: v["value"] for k, v in data["data"].items()}
            if symbols:
                return {s: rates.get(s, 1.0) for s in symbols if s in rates}
            return rates
        return None

