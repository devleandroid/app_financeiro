# Cliente para API de Bitcoin (CoinDesk)"""
import requests
import logging
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class BitcoinAPI:
    """Cliente para API pública do CoinGecko (mais confiável)"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def get_current_price(self, currency: str = "usd") -> Optional[Dict]:
        """
        Busca preço atual do Bitcoin usando CoinGecko
        """
        try:
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": "bitcoin",
                "vs_currencies": currency,
                "include_24hr_change": "true",
                "include_last_updated_at": "true"
            }
            
            logger.info(f"📡 Consultando CoinGecko para BTC/{currency.upper()}")
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if "bitcoin" in data:
                btc_data = data["bitcoin"]
                price = btc_data.get(currency, 0)
                change_24h = btc_data.get(f"{currency}_24h_change", 0)
                
                return {
                    "currency": currency.upper(),
                    "price": price,
                    "formatted": f"${price:,.2f}" if currency == "usd" else f"{price:,.2f}",
                    "change_24h": round(change_24h, 2),
                    "updated": datetime.fromtimestamp(btc_data.get("last_updated_at", 0)).strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp": datetime.now().isoformat(),
                    "source": "CoinGecko"
                }
            else:
                logger.warning("⚠️ Resposta inesperada da API, usando fallback")
                return self._get_mock_price(currency)
                
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout ao consultar CoinGecko")
            return self._get_mock_price(currency)
        except requests.exceptions.ConnectionError:
            logger.error("❌ Erro de conexão com CoinGecko")
            return self._get_mock_price(currency)
        except Exception as e:
            logger.error(f"❌ Erro ao buscar Bitcoin: {e}")
            return self._get_mock_price(currency)
    
    def _get_mock_price(self, currency: str = "usd") -> Dict:
        """Preço simulado para fallback"""
        import random
        price = random.uniform(60000, 70000)
        return {
            "currency": currency.upper(),
            "price": price,
            "formatted": f"${price:,.2f}",
            "change_24h": round(random.uniform(-5, 5), 2),
            "updated": "Simulated",
            "timestamp": datetime.now().isoformat(),
            "source": "Simulated (fallback)"
        }
    
    def get_historical_price(self, date: str, currency: str = "usd") -> Optional[Dict]:
        """
        Busca preço histórico (requer API paga)
        """
        # Por enquanto, retorna simulado
        return self._get_mock_price(currency)