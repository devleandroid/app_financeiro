import random
from datetime import datetime

class BitcoinService:
    """
    Serviço para buscar dados do Bitcoin.
    Por enquanto, vamos gerar dados simulados (mock).
    """
    def get_current_price(self, currency="USD"):
        """
        Simula a busca do preço atual do Bitcoin.
        """
        # Simula um preço entre $60,000 e $70,000
        price = random.uniform(60000, 70000)
        print(f"🟢 Preço do Bitcoin simulado: {price:.2f} {currency}")
        return {
            "currency": currency,
            "price": price,
            "timestamp": datetime.now().isoformat()
        }

    def get_historical_trend(self, days=30):
        """
        Simula uma tendência de alta ou baixa.
        """
        trend = random.choice(["alta", "baixa", "estável"])
        strength = random.uniform(0.1, 0.5)
        print(f"🟢 Tendência do Bitcoin simulada: {trend} com força {strength:.2f}")
        return {"trend": trend, "strength": strength}