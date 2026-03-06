# test_dados.py
import requests
import json

def testar_endpoint():
    """Testa o endpoint completo e valida os dados"""
    
    print("🔍 TESTANDO ENDPOINT COMPLETO")
    print("="*60)
    
    # Fazer requisição
    url = "http://localhost:8000/api/dados-completos?moedas=BRL,USD,EUR,GBP,CNY"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            dados = response.json()
            
            if dados.get('sucesso'):
                print("✅ Requisição bem sucedida!")
                
                # Validar dados de câmbio
                cambio = dados['dados_brutos']['cambio']
                print(f"\n💰 DADOS DE CÂMBIO (USD base):")
                for moeda, taxa in cambio.items():
                    print(f"   {moeda}: {taxa:.4f}")
                
                # Verificar se USD é 1.0
                if cambio.get('USD', 0) != 1.0:
                    print(f"⚠️  ALERTA: USD base deveria ser 1.0, mas é {cambio.get('USD')}")
                
                # Verificar cruzamentos importantes
                if 'BRL' in cambio and 'USD' in cambio:
                    usd_brl = cambio['BRL']
                    print(f"\n💵 Dólar Comercial: R$ {usd_brl:.2f}")
                    
                    if usd_brl < 4.5:
                        print("   ⚠️  Valor muito baixo para o padrão histórico")
                    elif usd_brl > 6.0:
                        print("   ⚠️  Valor muito alto para o padrão histórico")
                
                # Validar Bitcoin
                btc = dados['dados_brutos']['bitcoin']
                print(f"\n₿ BITCOIN:")
                print(f"   Preço: US$ {btc['preco']['price']:.2f}")
                print(f"   Tendência: {btc['tendencia']['trend']}")
                
                # Mostrar recomendações
                print(f"\n💡 RECOMENDAÇÕES:")
                for i, rec in enumerate(dados['recomendacoes'], 1):
                    print(f"\n   {i}. {rec['nome']}")
                    print(f"      Prazo: {rec['prazo']}")
                    print(f"      Risco: {rec['risco']}")
                    print(f"      Razão: {rec['razao']}")
                
                return dados
            else:
                print("❌ API retornou erro")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao backend")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return None

if __name__ == "__main__":
    dados = testar_endpoint()
    
    if dados:
        # Salvar para análise
        with open("dados_validados.json", "w") as f:
            json.dump(dados, f, indent=2, default=str)
        print(f"\n💾 Dados salvos em dados_validados.json")