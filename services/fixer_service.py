# services/fixer_service.py
import os
import requests
from dotenv import load_dotenv
import logging
from typing import Dict, List, Optional

# Carrega as chaves do arquivo .env
load_dotenv()

logger = logging.getLogger(__name__)

class FixerService:
    """
    Serviço para interagir com a API do Fixer.io.
    """
    def __init__(self):
        self.api_key = os.getenv("FIXER_API_KEY")
        # IMPORTANTE: Na versão gratuita, a base é sempre EUR
        self.base_url = "http://data.fixer.io/api/latest"
        
        if not self.api_key:
            logger.error("❌ FIXER_API_KEY não encontrada!")
            self._mostrar_erro_chave()

    def _mostrar_erro_chave(self):
        """Mostra mensagem de erro amigável"""
        print("\n" + "="*60)
        print("🔴 ERRO CRÍTICO: Chave da API Fixer.io não encontrada!")
        print("="*60)
        print("Para corrigir:")
        print("1. Acesse https://fixer.io/ e crie uma conta gratuita")
        print("2. Copie sua API key do dashboard")
        print("3. Crie um arquivo .env na raiz do projeto com:")
        print("   FIXER_API_KEY=sua_chave_aqui")
        print("="*60 + "\n")

    def get_latest_rates(self, symbols: List[str] = None) -> Optional[Dict]:
        """
        Busca as taxas de câmbio mais recentes (base EUR).
        Retorna None em caso de erro.
        """
        if not self.api_key:
            return None
            
        # Parâmetros da requisição
        params = {
            "access_key": self.api_key,
        }
        
        if symbols:
            params["symbols"] = ",".join(symbols)

        try:
            logger.info(f"📡 Chamando Fixer.io para moedas: {symbols}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Resposta do Fixer.io: {data}")
            
            if data.get("success"):
                logger.info("✅ Dados do Fixer.io obtidos com sucesso")
                
                # Mostrar informação importante sobre a base
                print(f"\n📊 Dados do Fixer.io (base: {data.get('base', 'EUR')})")
                print(f"📅 Data: {data.get('date')}")
                print(f"💰 Moedas recebidas: {list(data['rates'].keys())}")
                
                return data
            else:
                error_info = data.get("error", {})
                error_code = error_info.get('code')
                error_msg = error_info.get('info', 'Erro desconhecido')
                
                logger.error(f"Erro da API Fixer.io: {error_code} - {error_msg}")
                self._tratar_erro_api(error_code, error_msg)
                return None

        except requests.exceptions.Timeout:
            logger.error("Timeout na requisição ao Fixer.io")
            print("\n🔴 ERRO: Timeout na conexão com Fixer.io")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Erro de conexão com Fixer.io")
            print("\n🔴 ERRO: Não foi possível conectar ao Fixer.io")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return None

    def _tratar_erro_api(self, code: int, message: str):
        """Mostra mensagens amigáveis para erros comuns da API"""
        erros = {
            101: "Chave da API inválida ou não fornecida",
            104: "Limite de requisições mensal excedido (100/mês na conta gratuita)",
            105: "Assinatura gratuita não permite moeda base personalizada",
            201: "Moeda base inválida",
            202: "Moeda de símbolo inválida"
        }
        
        print(f"\n🔴 ERRO DA API FIXER ({code}):")
        print(f"   {erros.get(code, message)}")
        
        if code == 104:
            print("\n💡 Dica: O plano gratuito permite apenas 100 requisições por mês.")
            print("   Aguarde o próximo mês ou considere usar dados simulados para testes.")

    def converter_para_usd(self, rates_eur: Dict[str, float]) -> Dict[str, float]:
        """
        Converte taxas baseadas em EUR para base USD.
        
        Como a API gratuita sempre retorna base EUR, precisamos calcular:
        rate(USD para X) = rate(EUR para X) / rate(EUR para USD)
        
        Args:
            rates_eur: Dicionário com taxas base EUR
            
        Returns:
            Dicionário com taxas base USD
        """
        if not rates_eur or 'USD' not in rates_eur:
            print("🔴 ERRO: Não foi possível converter para USD - taxa USD não encontrada")
            return rates_eur
        
        # Taxa de EUR para USD
        eur_to_usd = rates_eur['USD']
        
        print(f"\n🔄 Convertendo taxas de EUR → USD")
        print(f"   Taxa EUR/USD: {eur_to_usd:.4f}")
        
        rates_usd = {}
        for moeda, taxa_eur in rates_eur.items():
            if moeda != 'USD':  # Não converter USD para USD
                # Fórmula: (EUR → MOEDA) / (EUR → USD) = USD → MOEDA
                taxa_usd = taxa_eur / eur_to_usd
                rates_usd[moeda] = round(taxa_usd, 4)
                print(f"   {moeda}: {taxa_eur:.4f} EUR → {taxa_usd:.4f} USD")
        
        # Adicionar USD como 1.0
        rates_usd['USD'] = 1.0
        
        return rates_usd

    def get_cruzamento_moedas(self, moeda_origem: str, moeda_destino: str, 
                              rates_usd: Dict[str, float]) -> Optional[float]:
        """
        Calcula taxa de cruzamento entre duas moedas quaisquer.
        
        Exemplo: BRL/JPY = (USD/BRL) / (USD/JPY)
        
        Args:
            moeda_origem: Moeda de origem (ex: 'BRL')
            moeda_destino: Moeda de destino (ex: 'JPY')
            rates_usd: Dicionário com taxas base USD
            
        Returns:
            Taxa de câmbio ou None se não for possível calcular
        """
        if moeda_origem not in rates_usd or moeda_destino not in rates_usd:
            print(f"🔴 ERRO: Moeda {moeda_origem} ou {moeda_destino} não disponível")
            return None
        
        # 1 USD = X moeda_origem
        # 1 USD = Y moeda_destino
        # Logo: 1 moeda_origem = (Y / X) moeda_destino
        
        taxa_origem_usd = rates_usd[moeda_origem]  # X
        taxa_destino_usd = rates_usd[moeda_destino]  # Y
        
        if taxa_origem_usd == 0:
            return None
            
        cruzamento = taxa_destino_usd / taxa_origem_usd
        return round(cruzamento, 4)