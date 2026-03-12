# Serviço unificado de Bitcoin com múltiplas fontes"""
import logging
from typing import Optional, Dict
from datetime import datetime
from .bitcoin_api import BitcoinAPI
from .alternative_api import AlternativeBitcoinAPI

logger = logging.getLogger(__name__)

class BitcoinService:
    """Serviço que tenta múltiplas fontes de dados BTC"""
    
    def __init__(self):
        self.primary_api = BitcoinAPI()
        self.alternative_api = AlternativeBitcoinAPI()
    
    def get_current_price(self, currency: str = "USD") -> Dict:
        """
        Tenta obter preço de múltiplas fontes em ordem
        """
        currency_lower = currency.lower()
        
        # Tentar CoinGecko primeiro
        try:
            result = self.primary_api.get_current_price(currency_lower)
            if result and result.get("source") != "Simulated (fallback)":
                logger.info(f"✅ Dados obtidos via CoinGecko")
                return result
        except Exception as e:
            logger.warning(f"⚠️ CoinGecko falhou: {e}")
        
        # Tentar APIs alternativas
        try:
            result = self.alternative_api.get_current_price(currency)
            if result:
                logger.info(f"✅ Dados obtidos via API alternativa")
                return result
        except Exception as e:
            logger.warning(f"⚠️ APIs alternativas falharam: {e}")
        
        # Fallback para dados simulados
        logger.warning("⚠️ Usando dados simulados de Bitcoin")
        import random
        price = random.uniform(60000, 70000)
        return {
            "currency": currency,
            "price": price,
            "formatted": f"${price:,.2f}",
            "change_24h": round(random.uniform(-5, 5), 2),
            "updated": "Simulated",
            "timestamp": datetime.now().isoformat(),
            "source": "Simulated (final fallback)"
        }
    
    def get_btc_brl(self) -> Optional[Dict]:
        """Método específico para BTC/BRL"""
        return self.get_current_price("BRL")

# Instância global para fácil acesso
bitcoin_service = BitcoinService()