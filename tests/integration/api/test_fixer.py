import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_fixer():
    api_key = os.getenv("FIXER_API_KEY")
    if not api_key:
        print("❌ ERRO: FIXER_API_KEY não encontrada no arquivo .env")
        print("Crie um arquivo .env com: FIXER_API_KEY=sua_chave_aqui")
        return
    
    print(f"🔑 API Key encontrada: {api_key[:5]}...{api_key[-5:]}")
    
    # Testar conexão com Fixer.io
    url = "http://data.fixer.io/api/latest"
    params = {
        "access_key": api_key,
        "base": "USD",
        "symbols": "BRL,EUR,GBP,CNY"
    }
    
    try:
        print("📡 Testando conexão com Fixer.io...")
        response = requests.get(url, params=params, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        data = response.json()
        if data.get("success"):
            print("✅ Conexão com Fixer.io OK!")
            print(f"📅 Data: {data.get('date')}")
            print(f"💰 Taxas: {data.get('rates')}")
        else:
            print("❌ Erro da API Fixer.io:")
            error = data.get("error", {})
            print(f"   Código: {error.get('code')}")
            print(f"   Tipo: {error.get('type')}")
            print(f"   Info: {error.get('info')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - Verifique sua internet")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_fixer()
