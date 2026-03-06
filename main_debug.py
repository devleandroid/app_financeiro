# main_debug.py (corrigido)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.fixer_service import FixerService
from services.bitcoin_service import BitcoinService
from logic.recomendador import Recomendador as Recomendador
import traceback
import logging  # <--- LINHA ADICIONADA

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="App de Recomendações Financeiras")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia os serviços
fixer_service = FixerService()
bitcoin_service = BitcoinService()
recomendador = Recomendador()

@app.get("/")
def raiz():
    logger.info("✅ Endpoint raiz acessado")
    return {"mensagem": "Bem-vindo à API de Recomendações Financeiras!"}

@app.get("/api/health")
def health_check():
    logger.info("✅ Health check acessado")
    return {"status": "ok"}

@app.get("/api/dados-completos")
def get_dados_completos(moedas: str = "BRL,EUR,GBP,CNY"):
    logger.info(f"📥 Requisição recebida com moedas: {moedas}")
    
    try:
        # 1. Busca dados do câmbio
        logger.debug("Buscando dados do Fixer.io...")
        lista_moedas = moedas.split(",")
        dados_cambio = fixer_service.get_latest_rates(symbols=lista_moedas)  # REMOVIDO base_currency

        if not dados_cambio:
            logger.error("❌ Falha ao obter dados do Fixer.io")
            raise HTTPException(status_code=503, detail="Falha ao obter dados de câmbio")
        
        logger.debug(f"✅ Dados do Fixer.io obtidos: {dados_cambio.get('rates', {})}")

        # 2. Busca dados do Bitcoin
        logger.debug("Buscando dados do Bitcoin...")
        dados_bitcoin_preco = bitcoin_service.get_current_price()
        dados_bitcoin_tendencia = bitcoin_service.get_historical_trend()
        
        logger.debug(f"✅ Dados do Bitcoin obtidos: preço={dados_bitcoin_preco.get('price')}")

        # 3. CONVERTER para USD base (importante!)
        logger.debug("Convertendo taxas para base USD...")
        rates_usd = fixer_service.converter_para_usd(dados_cambio["rates"])

        # 4. Junta todos os dados
        dados_consolidados = {
            "cambio": rates_usd,  # USAR VERSÃO CONVERTIDA
            "cambio_original": {
                "base": dados_cambio["base"],
                "date": dados_cambio["date"],
                "rates_eur": dados_cambio["rates"]
            },
            "data_cambio": dados_cambio["date"],
            "bitcoin": {
                "preco": dados_bitcoin_preco,
                "tendencia": dados_bitcoin_tendencia
            }
        }

        # 5. Gera recomendações
        logger.debug("Gerando recomendações...")
        recomendacoes = recomendador.gerar_recomendacoes(dados_consolidados)
        logger.debug(f"✅ {len(recomendacoes)} recomendações geradas")

        return {
            "sucesso": True,
            "dados_brutos": dados_consolidados,
            "recomendacoes": recomendacoes
        }

    except HTTPException as e:
        logger.error(f"❌ HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Para testar diretamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)