# APIs alternativas para fallback"""
import requests
import logging
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class AlternativeBitcoinAPI:
    """Cliente para APIs alternativas de Bitcoin"""
    
    def __init__(self):
        self.apis = [
            {
                "name": "Blockchain.info",
                "url": "https://blockchain.info/ticker",
                "parser": self._parse_blockchain
            },
            {
                "name": "Mempool.space",
                "url": "https://mempool.space/api/v1/prices",
                "parser": self._parse_mempool
            }
        ]
    
    def get_current_price(self, currency: str = "USD") -> Optional[Dict]:
        """Tenta várias APIs até conseguir uma resposta"""
        
        for api in self.apis:
            try:
                logger.info(f"📡 Tentando API: {api['name']}")
                response = requests.get(api["url"], timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    price_data = api["parser"](data, currency)
                    
                    if price_data:
                        logger.info(f"✅ Sucesso com {api['name']}")
                        return price_data
                        
            except Exception as e:
                logger.warning(f"⚠️ {api['name']} falhou: {e}")
                continue
        
        logger.error("❌ Todas as APIs falharam")
        return None
    
    def _parse_blockchain(self, data: dict, currency: str = "USD") -> Optional[Dict]:
        """Parser para Blockchain.info"""
        if currency in data:
            return {
                "currency": currency,
                "price": data[currency]["last"],
                "formatted": f"${data[currency]['last']:,.2f}",
                "symbol": data[currency]["symbol"],
                "source": "Blockchain.info"
            }
        return None
    
    def _parse_mempool(self, data: dict, currency: str = "USD") -> Optional[Dict]:
        """Parser para Mempool.space"""
        if currency in data:
            return {
                "currency": currency,
                "price": data[currency],
                "formatted": f"${data[currency]:,.2f}",
                "source": "Mempool.space"
            }
        return None