# test_fixer_real.py
from services.fixer_service import FixerService
import json
from pprint import pprint

def testar_fixer():
    """Testa a API Fixer e valida os cálculos"""
    
    print("="*60)
    print("🔍 TESTE DA INTEGRAÇÃO COM FIXER.IO")
    print("="*60)
    
    # Inicializar serviço
    fixer = FixerService()
    
    # Moedas de interesse
    moedas = ["USD", "BRL", "EUR", "GBP", "CNY", "JPY", "RUB"]
    
    print(f"\n📌 Moedas solicitadas: {moedas}")
    
    # Buscar dados da API
    dados = fixer.get_latest_rates(symbols=moedas)
    
    if not dados:
        print("\n❌ Falha ao obter dados da API Fixer")
        print("\n🔄 Usando dados simulados para teste...")
        dados = {
            "success": True,
            "base": "EUR",
            "date": "2024-01-01",
            "rates": {
                "USD": 1.08,
                "BRL": 5.45,
                "EUR": 1.0,
                "GBP": 0.86,
                "CNY": 7.75,
                "JPY": 162.0,
                "RUB": 98.5
            }
        }
    
    print("\n📊 Dados Recebidos:")
    print(f"   Base: {dados.get('base')}")
    print(f"   Data: {dados.get('date')}")
    print(f"   Taxas (EUR base):")
    for moeda, taxa in dados['rates'].items():
        print(f"      {moeda}: {taxa:.4f}")
    
    # Converter para USD base
    print("\n🔄 Convertendo para base USD...")
    rates_usd = fixer.converter_para_usd(dados['rates'])
    
    print("\n💰 Taxas (USD base):")
    for moeda, taxa in sorted(rates_usd.items()):
        print(f"   {moeda}: {taxa:.4f}")
    
    # Validar cálculos
    print("\n✅ VALIDAÇÃO DOS CÁLCULOS:")
    
    # 1 USD deve ser 1.0
    assert rates_usd['USD'] == 1.0, "ERRO: USD não é 1.0"
    print("   ✓ USD base = 1.0")
    
    # Verificar conversão circular: USD → EUR → USD
    eur_usd = rates_usd['EUR']  # USD para EUR
    usd_eur = 1.0 / eur_usd if eur_usd != 0 else 0  # EUR para USD (calculado)
    print(f"   ✓ USD/EUR: {eur_usd:.4f} | EUR/USD: {usd_eur:.4f}")
    
    # Testar cruzamentos
    print("\n🔄 CRUZAMENTOS ENTRE MOEDAS:")
    
    pares = [
        ("BRL", "USD"),  # Real para Dólar
        ("USD", "BRL"),  # Dólar para Real
        ("EUR", "BRL"),  # Euro para Real
        ("BRL", "JPY"),  # Real para Iene
        ("GBP", "BRL"),  # Libra para Real
        ("CNY", "BRL"),  # Yuan para Real
    ]
    
    for origem, destino in pares:
        if origem in rates_usd and destino in rates_usd:
            taxa = fixer.get_cruzamento_moedas(origem, destino, rates_usd)
            if taxa:
                print(f"   {origem}/{destino}: {taxa:.4f}")
                # Mostrar significado prático
                if origem == "USD" and destino == "BRL":
                    print(f"      → 1 USD = R$ {taxa:.2f}")
                elif origem == "BRL" and destino == "USD":
                    print(f"      → R$ 1 = US$ {taxa:.4f}")
                elif origem == "EUR" and destino == "BRL":
                    print(f"      → 1 EUR = R$ {taxa:.2f}")
    
    # Estatísticas
    print("\n📈 RESUMO ECONÔMICO:")
    if 'BRL' in rates_usd:
        dolar_real = rates_usd['BRL']
        print(f"   Dólar Comercial: R$ {dolar_real:.2f}")
        
        # Classificação do Real
        if dolar_real < 5.0:
            print(f"   🇧🇷 Real FORTE (abaixo de R$5.00)")
        elif dolar_real > 5.5:
            print(f"   🇧🇷 Real FRACO (acima de R$5.50)")
        else:
            print(f"   🇧🇷 Real ESTÁVEL (entre R$5.00 e R$5.50)")
    
    if 'BTC' in rates_usd:  # Se tivermos Bitcoin
        print(f"   Bitcoin: US$ {rates_usd['BTC']:.2f}")
    
    print("\n" + "="*60)
    return rates_usd

if __name__ == "__main__":
    taxas_usd = testar_fixer()
    
    # Salvar para referência
    with open("taxas_referencia.json", "w") as f:
        json.dump(taxas_usd, f, indent=2)
    print("\n💾 Taxas salvas em taxas_referencia.json")