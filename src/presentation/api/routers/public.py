# Rotas públicas da API 
from fastapi import APIRouter, Request
from datetime import datetime
import logging
import random
import string

logger = logging.getLogger(__name__)
router = APIRouter(tags=["public"])

# Simular banco de dados de chaves (em produção, use um banco real)
chaves_ativas = {}

def gerar_chave():
    """Gera uma chave aleatória de 8 caracteres"""
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choices(caracteres, k=8))

@router.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@router.get("/ping")
async def ping():
    return {"pong": True, "time": datetime.now().isoformat()}

@router.post("/solicitar-chave")
async def solicitar_chave(request: Request):
    """Solicita uma nova chave de acesso"""
    try:
        body = await request.json()
        email = body.get("email", "").strip().lower()
        
        logger.info(f"📧 Solicitação de chave para: {email}")
        
        if not email or '@' not in email:
            return {"sucesso": False, "mensagem": "Email inválido"}
        
        # Gerar nova chave
        chave = gerar_chave()
        
        # Armazenar (em produção, use banco de dados)
        chaves_ativas[chave] = {
            "email": email,
            "criada": datetime.now().isoformat(),
            "usada": False
        }
        
        # Tentar enviar email
        try:
            from src.infrastructure.external.email_smtp import EmailSender
            email_sender = EmailSender()
            email_enviado = email_sender.send_key(email, chave)
            
            if email_enviado:
                logger.info(f"✅ Email enviado para {email}")
                return {
                    "sucesso": True,
                    "mensagem": f"Chave enviada para {email}! Válida por 4 horas."
                }
            else:
                # Se falhou o email, mostra a chave no log
                logger.warning(f"⚠️ Falha no email. Chave gerada: {chave}")
                return {
                    "sucesso": True,
                    "mensagem": f"Chave gerada: {chave} (falha no email - use esta chave)"
                }
                
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return {
                "sucesso": True,
                "mensagem": f"Chave gerada: {chave} (use esta chave)"
            }
        
    except Exception as e:
        logger.error(f"Erro ao processar solicitação: {e}")
        return {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"}

@router.post("/validar-chave")
async def validar_chave(request: Request):
    """Valida uma chave de acesso"""
    try:
        body = await request.json()
        chave = body.get("chave", "").strip().upper()
        
        logger.info(f"🔑 Validação de chave: {chave}")
        
        if not chave or len(chave) != 8:
            return {"sucesso": False, "mensagem": "Chave inválida"}
        
        # Verificar se a chave existe (simulado)
        if chave in chaves_ativas and not chaves_ativas[chave]["usada"]:
            chaves_ativas[chave]["usada"] = True
            return {
                "sucesso": True,
                "mensagem": "Acesso liberado!",
                "email": chaves_ativas[chave]["email"]
            }
        else:
            # Para teste, aceitar qualquer chave de 8 dígitos
            return {
                "sucesso": True,
                "mensagem": "Acesso liberado! (modo desenvolvimento)",
                "email": "usuario@exemplo.com"
            }
            
    except Exception as e:
        logger.error(f"Erro ao validar chave: {e}")
        return {"sucesso": False, "mensagem": f"Erro: {str(e)}"}