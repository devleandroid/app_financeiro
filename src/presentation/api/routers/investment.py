# Rotas de investmento com dados reais 
from fastapi import APIRouter
import logging
from datetime import datetime
from src.infrastructure.external.apis.fixer_api import FixerAPI
from src.infrastructure.external.apis.bitcoin_service import bitcoin_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/investment", tags=["investment"])

# Instanciar APIs
fixer_api = FixerAPI()

@router.get("/dados")
async def get_dados(moedas: str = "BRL,USD,EUR"):
    """Retorna dados reais de câmbio"""
    try:
        moedas_lista = [m.strip() for m in moedas.split(",")]
        logger.info(f"📊 Buscando dados reais para: {moedas_lista}")
        
        # Buscar dados da Fixer.io (com fallback automático)
        dados_fixer = fixer_api.get_latest_rates(symbols=moedas_lista)
        
        # Buscar dados do Bitcoin
        bitcoin_data = bitcoin_service.get_current_price("USD")
        
        # Verificar se temos dados (reais ou simulados)
        if isinstance(dados_fixer, dict):
            # Se tem a chave 'source', sabemos a origem
            fonte = dados_fixer.get("source", "Desconhecida")
            
            resultado = {
                "sucesso": True,
                "dados": dados_fixer.get("rates", dados_fixer),
                "data": dados_fixer.get("date", datetime.now().strftime("%Y-%m-%d")),
                "base": dados_fixer.get("base", "USD"),
                "bitcoin": bitcoin_data,
                "fonte": fonte,
                "timestamp": datetime.now().isoformat()
            }
            
            if fonte == "Fixer.io":
                logger.info(f"✅ Dados reais do Fixer.io: {list(dados_fixer['rates'].keys())}")
            elif "alternativa" in fonte.lower():
                logger.info(f"✅ Dados de API alternativa: {fonte}")
            else:
                logger.warning(f"⚠️ Usando dados simulados")
            
            return resultado
        else:
            # Fallback extremo
            logger.error("❌ Nenhuma fonte de dados disponível")
            return {
                "sucesso": False,
                "erro": "Nenhuma fonte de dados disponível",
                "dados": {
                    "USD": 1.0,
                    "BRL": 5.25,
                    "EUR": 0.92
                },
                "bitcoin": bitcoin_data,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados: {e}")
        return {
            "sucesso": False,
            "erro": str(e),
            "dados": {
                "USD": 1.0,
                "BRL": 5.25,
                "EUR": 0.92
            },
            "bitcoin": bitcoin_service.get_current_price("USD")
        }

@router.get("/recomendacoes")
async def get_recomendacoes():
    """Retorna recomendações baseadas nos dados reais"""
    
    try:
        # Buscar dados atuais
        dados = fixer_api.get_latest_rates(symbols=["USD", "BRL", "EUR", "GBP", "JPY"])
        bitcoin = bitcoin_service.get_current_price("USD")
        
        recomendacoes = []
        
        if isinstance(dados, dict):
            rates = dados.get("rates", dados)
            
            # Recomendação baseada no Real
            if "BRL" in rates:
                usd_brl = rates["BRL"]
                if usd_brl < 5.0:
                    recomendacoes.append({
                        "nome": "🇧🇷 Ações de Exportação",
                        "prazo": "Curto Prazo",
                        "risco": "Médio",
                        "razao": f"Real forte (USD/BRL = {usd_brl:.2f}) favorece empresas exportadoras"
                    })
                elif usd_brl > 5.5:
                    recomendacoes.append({
                        "nome": "🇧🇷 Títulos Indexados",
                        "prazo": "Curto Prazo",
                        "risco": "Baixo",
                        "razao": f"Real fraco (USD/BRL = {usd_brl:.2f}) - proteção cambial"
                    })
            
            # Recomendação baseada no Euro
            if "EUR" in rates:
                eur_usd = 1 / rates["EUR"] if rates["EUR"] > 0 else 0
                if eur_usd > 1.10:
                    recomendacoes.append({
                        "nome": "🇪🇺 Bonds Europeus",
                        "prazo": "Longo Prazo",
                        "risco": "Baixo",
                        "razao": f"Euro forte (EUR/USD = {eur_usd:.2f}) - títulos alemães"
                    })
            
            # Recomendação baseada no Iene
            if "JPY" in rates:
                usd_jpy = rates["JPY"]
                if usd_jpy > 150:
                    recomendacoes.append({
                        "nome": "🇯🇵 Exportadoras Japonesas",
                        "prazo": "Curto Prazo",
                        "risco": "Médio",
                        "razao": f"Iene desvalorizado (USD/JPY = {usd_jpy:.0f}) beneficia exportações"
                    })
        
        # Bitcoin
        if bitcoin and bitcoin.get("price", 0) < 65000:
            recomendacoes.append({
                "nome": "₿ Bitcoin ETF",
                "prazo": "Longo Prazo",
                "risco": "Alto",
                "razao": f"Bitcoin abaixo de $65k ({bitcoin.get('formatted', 'N/A')})"
            })
        
        # Recomendações genéricas
        recomendacoes_base = [
            {
                "nome": "🌍 ETF Global",
                "prazo": "Longo Prazo",
                "risco": "Médio",
                "razao": "Diversificação internacional"
            },
            {
                "nome": "🏦 Fundos Imobiliários",
                "prazo": "Médio Prazo",
                "risco": "Médio",
                "razao": "Renda passiva mensal"
            },
            {
                "nome": "💰 Ouro (GLD)",
                "prazo": "Longo Prazo",
                "risco": "Baixo",
                "razao": "Proteção contra volatilidade cambial"
            }
        ]
        
        recomendacoes.extend(recomendacoes_base)
        
        return {
            "sucesso": True,
            "recomendacoes": recomendacoes[:5],
            "total": len(recomendacoes),
            "fontes": {
                "cambio": dados.get("source", "Fixer.io"),
                "bitcoin": bitcoin.get("source", "CoinGecko")
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar recomendações: {e}")
        return {
            "sucesso": True,
            "recomendacoes": [
                {
                    "nome": "Tesouro Direto",
                    "prazo": "Longo Prazo",
                    "risco": "Baixo",
                    "razao": "Proteção contra inflação"
                },
                {
                    "nome": "Ações de Bancos",
                    "prazo": "Curto Prazo",
                    "risco": "Médio",
                    "razao": "Cenário de juros altos"
                }
            ]
        }