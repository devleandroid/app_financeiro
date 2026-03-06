import os
import requests
from dotenv import load_dotenv
import logging

# Carrega as chaves do arquivo .env
load_dotenv()

logger = logging.getLogger(__name__)

class FixerService:
    """
    Serviço para interagir com a API do Fixer.io.
    """
    def __init__(self):
        self.api_key = os.getenv("FIXER_API_KEY")
        self.base_url = "http://data.fixer.io/api/latest"
        
        if not self.api_key:
            logger.error("❌ FIXER_API_KEY não encontrada!")
            print("\n" + "="*50)
            print("🔴 ERRO CRÍTICO: Chave da API Fixer.io não encontrada!")
            print("="*50)
            print("Crie um arquivo .env na raiz do projeto com:")
            print("FIXER_API_KEY=sua_chave_aqui")
            print("\nPara obter uma chave gratuita, acesse: https://fixer.io/")
            print("="*50 + "\n")

    def get_latest_rates(self, base_currency="USD", symbols=None):
        """
        Busca as taxas de câmbio mais recentes.
        """
        if not self.api_key:
            logger.error("API key não configurada")
            return None
            
        # Parâmetros da requisição
        params = {
            "access_key": self.api_key,
            "base": base_currency
        }
        
        if symbols:
            params["symbols"] = ",".join(symbols)

        try:
            logger.info(f"Chamando Fixer.io com moedas: {symbols}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            
            # Log da resposta para debug
            logger.debug(f"Resposta do Fixer.io: {data}")
            
            if data.get("success"):
                logger.info("Dados do Fixer.io obtidos com sucesso")
                return data
            else:
                error_info = data.get("error", {})
                error_msg = error_info.get('info', 'Erro desconhecido')
                error_code = error_info.get('code', 'sem código')
                
                logger.error(f"Erro da API Fixer.io: {error_code} - {error_msg}")
                
                # Mensagens amigáveis para erros comuns
                if error_code == 101:
                    print("\n🔴 ERRO: Chave da API inválida ou não fornecida")
                    print("   Verifique se você cadastrou a chave correta no arquivo .env")
                elif error_code == 104:
                    print("\n🔴 ERRO: Limite de requisições excedido")
                    print("   A conta gratuita permite apenas 100 requisições por mês")
                elif error_code == 105:
                    print("\n🔴 ERRO: Assinatura gratuita não permite moeda base personalizada")
                    print("   Na conta gratuita, a moeda base é fixa em EUR")
                    print("   Use 'EUR' como base ou faça o cálculo manualmente")
                
                return None

        except requests.exceptions.Timeout:
            logger.error("Timeout na requisição ao Fixer.io")
            print("\n🔴 ERRO: Timeout na conexão com Fixer.io")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Erro de conexão com Fixer.io")
            print("\n🔴 ERRO: Não foi possível conectar ao Fixer.io")
            print("   Verifique sua conexão com a internet")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            return None
        except ValueError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            return None