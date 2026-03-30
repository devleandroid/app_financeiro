# Cliente real para API Fixer.io com fallback para APIs alternativas 
import os
import requests
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FixerAPI:
    """Cliente para API Fixer.io com fallback para APIs alternativas"""
    
    def __init__(self):
        self.api_key = os.getenv("FIXER_API_KEY")
        self.base_url = "http://data.fixer.io/api/latest"
        self.alternatives = None
        
        # Carregar APIs alternativas sob demanda
        self._load_alternatives()
    
    def _load_alternatives(self):
        """Carrega o módulo de APIs alternativas (lazy loading)"""
        try:
            from .exchange_alternatives import ExchangeAlternatives
            self.alternatives = ExchangeAlternatives()
            logger.info("✅ APIs alternativas carregadas")
        except ImportError as e:
            logger.warning(f"⚠️ Não foi possível carregar APIs alternativas: {e}")
    
    def get_latest_rates(self, symbols: List[str] = None) -> Optional[Dict]:
        """
        Busca taxas de câmbio reais da API Fixer.io
        Com fallback para APIs alternativas
        """
        # Tenta Fixer.io primeiro
        if self.api_key:
            result = self._try_fixer(symbols)
            if result:
                return result
        
        # Se Fixer falhou, tenta APIs alternativas
        logger.info("🔄 Tentando APIs alternativas...")
        if self.alternatives:
            result = self.alternatives.get_rates(symbols)
            if result:
                logger.info(f"✅ Dados obtidos via API alternativa: {result.get('source')}")
                return result
        
        # Último recurso: dados simulados
        logger.warning("⚠️ Usando dados simulados (último recurso)")
        return self._get_mock_rates(symbols)
    
    def _try_fixer(self, symbols: List[str] = None) -> Optional[Dict]:
        """Tenta obter dados da Fixer.io"""
        try:
            params = {"access_key": self.api_key}
            
            if symbols:
                params["symbols"] = ",".join(symbols)
            
            logger.info(f"📡 Consultando Fixer.io para moedas: {symbols}")
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if data.get("success"):
                rates = data["rates"]
                logger.info(f"✅ Dados recebidos do Fixer.io: {list(rates.keys())}")
                
                # Converter para USD base
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
                        "source": "Fixer.io"
                    }
                
                return {
                    "base": "EUR",
                    "date": data["date"],
                    "rates": rates,
                    "source": "Fixer.io"
                }
            else:
                error = data.get("error", {})
                error_code = error.get("code")
                
                if error_code == 104:
                    logger.warning("⚠️ Limite do Fixer.io excedido. Tentando alternativas...")
                else:
                    logger.error(f"❌ Erro Fixer.io: {error}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao acessar Fixer.io: {e}")
            return None
    
    def _get_mock_rates(self, symbols: List[str] = None) -> Dict:
        """Dados simulados para fallback final"""
        logger.warning("⚠️ Usando dados simulados (fallback final)")
        
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
        """Busca taxas históricas (requer plano pago)"""
        # Por enquanto, retorna dados simulados
        return self._get_mock_rates(symbols)