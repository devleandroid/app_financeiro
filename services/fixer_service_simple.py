import random
from datetime import datetime

class FixerService:
    """
    Versão simplificada que gera dados simulados
    """
    def get_latest_rates(self, base_currency="USD", symbols=None):
        print("⚠️ Usando dados simulados do Fixer.io (modo de teste)")
        
        # Gerar taxas simuladas
        taxas_simuladas = {
            "BRL": round(random.uniform(4.8, 5.2), 4),
            "EUR": round(random.uniform(0.85, 0.95), 4),
            "GBP": round(random.uniform(0.75, 0.85), 4),
            "CNY": round(random.uniform(6.8, 7.2), 4),
            "JPY": round(random.uniform(140, 150), 2),
            "CAD": round(random.uniform(1.3, 1.4), 4),
            "AUD": round(random.uniform(1.4, 1.5), 4),
            "RUB": round(random.uniform(90, 100), 2)
        }
        
        # Filtrar apenas as moedas solicitadas
        if symbols:
            rates = {moeda: taxas_simuladas.get(moeda, 1.0) for moeda in symbols}
        else:
            rates = taxas_simuladas
        
        return {
            "success": True,
            "base": base_currency,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "rates": rates
        }