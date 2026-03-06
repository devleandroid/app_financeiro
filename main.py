# main.py
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets
import os
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv
from functools import lru_cache
import time

# Importar nossos módulos
from database import db
from services.email_service import email_service
from services.fixer_service import FixerService
from services.bitcoin_service import BitcoinService
from logic.recomendador import Recomendador


# Cache simples
ultima_resposta = None
ultimo_tempo = 0


# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# INICIALIZAR FASTAPI
# ============================================
app = FastAPI(
    title="InvestSmart API",
    description="API para análise de investimentos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# MODELOS DE DADOS
# ============================================
class SolicitarChaveModel(BaseModel):
    email: str

class ValidarChaveModel(BaseModel):
    chave: str

# ============================================
# AUTENTICAÇÃO ADMIN
# ============================================
security = HTTPBasic()
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "mude_esta_senha")

def verificar_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verifica se é o admin"""
    correct_user = secrets.compare_digest(credentials.username, ADMIN_USER)
    correct_pass = secrets.compare_digest(credentials.password, ADMIN_PASS)
    
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=401,
            detail="Acesso negado"
        )
    return credentials.username

# ============================================
# INICIALIZAR SERVIÇOS
# ============================================
fixer_service = FixerService()
bitcoin_service = BitcoinService()
recomendador = Recomendador()

# ============================================
# ENDPOINTS PÚBLICOS
# ============================================

@app.get("/")
def raiz():
    """Endpoint raiz"""
    return {
        "app": "InvestSmart API",
        "versao": "1.0.0",
        "status": "online",
        "endpoints": [
            "/api/solicitar-chave",
            "/api/validar-chave",
            "/api/dados-completos",
            "/api/admin/relatorio-semanal"
        ]
    }

@app.get("/api/health")
def health_check():
    """Verifica se a API está funcionando"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/api/solicitar-chave")
async def solicitar_chave(dados: SolicitarChaveModel, request: Request):
    """
    Solicita uma nova chave de acesso
    - Valida o email
    - Gera chave única de 8 caracteres
    - Envia por email
    - Chave válida por 4 horas
    """
    try:
        email = dados.email.strip().lower()
        
        # Validação básica de email
        if '@' not in email or '.' not in email:
            return {
                "sucesso": False,
                "mensagem": "Email inválido. Digite um email válido."
            }
        
        logger.info(f"📧 Solicitando chave para: {email}")
        
        # Gerar chave no banco de dados
        sucesso, mensagem, chave = db.solicitar_chave(
            email=email,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        if sucesso and chave:
            # Enviar email com a chave
            email_enviado = email_service.enviar_chave_acesso(
                email_destino=email,
                chave=chave,
                horas_validade=4
            )
            
            if email_enviado:
                return {
                    "sucesso": True,
                    "mensagem": "Chave enviada para seu email! Válida por 4 horas. Verifique sua caixa de entrada e spam."
                }
            else:
                return {
                    "sucesso": True,
                    "mensagem": f"Chave gerada: {chave} (Falha no email - use esta chave)"
                }
        else:
            return {
                "sucesso": False,
                "mensagem": mensagem
            }
            
    except Exception as e:
        logger.error(f"Erro ao solicitar chave: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro interno: {str(e)}"
        }

@app.post("/api/validar-chave")
async def validar_chave(dados: ValidarChaveModel, request: Request):
    """
    Valida uma chave de acesso
    - Verifica se chave existe
    - Verifica se não expirou (4h)
    - Verifica se não foi usada
    - Registra o acesso
    """
    try:
        chave = dados.chave.strip().upper()
        
        logger.info(f"🔑 Validando chave: {chave}")
        
        sucesso, mensagem, email = db.validar_chave(
            chave=chave,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "sucesso": sucesso,
            "mensagem": mensagem,
            "email": email
        }
        
    except Exception as e:
        logger.error(f"Erro ao validar chave: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro interno: {str(e)}"
        }

@app.get("/api/dados-completos")
def get_dados_completos(moedas: str = "BRL,EUR,GBP,CNY"):
    global ultima_resposta, ultimo_tempo
    
    # Se já temos dados com menos de 5 minutos, retorna do cache
    if ultima_resposta and (time.time() - ultimo_tempo) < 300:
        logger.info("📦 Retornando dados do cache")
        return ultima_resposta
    
    try:
        lista_moedas = moedas.split(",")
        
        # Buscar dados com timeout menor
        import asyncio
        try:
            dados_cambio = asyncio.run(
                asyncio.wait_for(
                    asyncio.to_thread(fixer_service.get_latest_rates, lista_moedas),
                    timeout=8.0
                )
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Timeout na API Fixer")
        
        if not dados_cambio:
            raise HTTPException(status_code=503, detail="Falha ao obter dados de câmbio")
        
        # Resto do processamento...
        rates_usd = fixer_service.converter_para_usd(dados_cambio["rates"])
        
        dados_bitcoin_preco = bitcoin_service.get_current_price()
        dados_bitcoin_tendencia = bitcoin_service.get_historical_trend()
        
        dados_consolidados = {
            "cambio": rates_usd,
            "data_cambio": dados_cambio["date"],
            "bitcoin": {
                "preco": dados_bitcoin_preco,
                "tendencia": dados_bitcoin_tendencia
            }
        }
        
        recomendacoes = recomendador.gerar_recomendacoes(dados_consolidados)
        
        resposta = {
            "sucesso": True,
            "dados_brutos": dados_consolidados,
            "recomendacoes": recomendacoes
        }
        
        # Atualizar cache
        ultima_resposta = resposta
        ultimo_tempo = time.time()
        
        return resposta
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ENDPOINTS ADMIN (PROTEGIDOS)
# ============================================

@app.get("/api/admin/relatorio-semanal")
def relatorio_semanal(admin: str = Depends(verificar_admin)):
    """Gera relatório semanal completo - SÓ PARA ADMIN"""
    try:
        relatorio = db.gerar_relatorio_semanal()
        return {
            "sucesso": True,
            "relatorio": relatorio
        }
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        return {
            "sucesso": False,
            "erro": str(e)
        }

@app.get("/api/admin/solicitacoes")
def listar_solicitacoes(admin: str = Depends(verificar_admin)):
    """Lista todas as solicitações de chave - SÓ PARA ADMIN"""
    try:
        df = db.listar_todas_solicitacoes()
        return {
            "sucesso": True,
            "dados": df.to_dict('records')
        }
    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e)
        }

@app.get("/api/admin/acessos")
def listar_acessos(admin: str = Depends(verificar_admin)):
    """Lista todos os acessos ao dashboard - SÓ PARA ADMIN"""
    try:
        df = db.listar_todos_acessos()
        return {
            "sucesso": True,
            "dados": df.to_dict('records')
        }
    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e)
        }

# ============================================
# EXECUÇÃO
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)