"""Rotas públicas da API"""
from fastapi import APIRouter, Request
from datetime import datetime, timedelta
import logging
import string
import secrets
import sqlite3
import re
import os

# Configuração do logger
logger = logging.getLogger(__name__)

# Instância do router
router = APIRouter(tags=["public"])

# Importação do serviço de email
from src.infrastructure.external.email_smtp import EmailSender
email_sender = EmailSender()

# Verificar se está em ambiente de desenvolvimento
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def gerar_chave() -> str:
    """
    Gera uma chave de acesso aleatória de 8 caracteres.
    
    Returns:
        str: Chave aleatória composta por letras maiúsculas e números.
    
    Exemplo:
        >>> gerar_chave()
        'A1B2C3D4'
    """
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(8))

""" Valida o formato do email usando expressão regular.  """
def validar_email(email: str) -> bool:
    if not email or '@' not in email:
        return False
    
    # Padrão regex para validação robusta de email
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(padrao, email):
        return False
    
    # Verificar se o domínio tem pelo menos um ponto e extensão válida
    dominio = email.split('@')[1]
    if '.' not in dominio:
        return False
    
    # Verificar extensão do domínio (mínimo 2 caracteres)
    extensao = dominio.split('.')[-1]
    if len(extensao) < 2:
        return False
    
    return True

""" Salva a solicitação de chave no banco de dados."""
def salvar_solicitacao(email: str, chave: str, ip: str = None) -> None:
    conn = sqlite3.connect("acessos.db")
    cursor = conn.cursor()
    
    # Criar tabela se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            key TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            ip TEXT,
            user_agent TEXT
        )
    ''')
    
    # Calcular data de expiração (4 horas a partir de agora)
    now = datetime.now()
    expires_at = now + timedelta(hours=4)
    
    # Inserir no banco
    cursor.execute('''
        INSERT INTO access_keys (email, key, created_at, expires_at, used, ip)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (email, chave, now.isoformat(), expires_at.isoformat(), 0, ip))
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Solicitação salva no banco: {email}")


@router.post("/solicitar-chave")
async def solicitar_chave(request: Request):
    """Solicita uma nova chave de acesso"""
    try:
        # Extrair email do corpo da requisição
        body = await request.json()
        email = body.get("email", "").strip().lower()
        
        logger.info(f"📧 Solicitação de chave para: {email}")
        
        # Validar formato do email
        if not validar_email(email):
            logger.warning(f"❌ Tentativa de email inválido: {email}")
            return {
                "sucesso": False, 
                "mensagem": "Email inválido. Use um formato válido como nome@dominio.com"
            }
        
        # Verificar se já existe chave válida (não expirada)
        conn = sqlite3.connect("acessos.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT key, expires_at FROM access_keys 
            WHERE email = ? AND datetime(expires_at) > datetime('now')
            ORDER BY created_at DESC LIMIT 1
        ''', (email,))
        existing = cursor.fetchone()
        conn.close()
        
        # Se já existe chave válida, retorna mensagem informativa
        if existing:
            chave_existente, expira_em = existing
            expiracao = datetime.fromisoformat(expira_em)
            horas_restantes = (expiracao - datetime.now()).total_seconds() / 3600
            return {
                "sucesso": False,
                "mensagem": f"Você já possui uma chave válida. Expira em {horas_restantes:.1f} horas."
                # NOTA: A chave NÃO é retornada por segurança
            }
        
        # Gerar nova chave
        chave = gerar_chave()

        # ⚠️ SEGURANÇA: A chave só é mostrada no LOG do BACKEND (apenas desenvolvedor)
        # Em produção, isso pode ser desabilitado com a variável ENVIRONMENT=production
        if ENVIRONMENT == "development":
            logger.info(f"🔑 CHAVE GERADA (apenas para desenvolvimento): {chave}")
        else:
            logger.info(f"🔑 Chave gerada e enviada para {email}")
        
        # Salvar no banco de dados
        ip = request.client.host if request.client else None
        salvar_solicitacao(email, chave, ip)
        
        # Enviar chave por email (única forma segura para o usuário receber a chave)
        email_enviado = email_sender.send_key(email, chave)
        
        if not email_enviado:
            logger.warning(f"⚠️ Falha no envio de email para {email}")
            # Em desenvolvimento, mostrar a chave no console como fallback
            if ENVIRONMENT == "development":
                print(f"\n{'='*60}")
                print(f"🔑 CHAVE DE ACESSO (FALHA NO EMAIL): {chave}")
                print(f"📧 PARA: {email}")
                print(f"{'='*60}\n")
        
        logger.info(f"✅ Chave gerada e enviada para {email}")
        
        # Retornar apenas confirmação, sem expor a chave
        return {
            "sucesso": True,
            "mensagem": f"Chave enviada para {email}! Válida por 4 horas. Verifique sua caixa de entrada e spam."
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar solicitação: {e}")
        return {"sucesso": False, "mensagem": f"Erro interno. Tente novamente mais tarde."}


@router.post("/validar-chave")
async def validar_chave(request: Request):
    """Valida uma chave de acesso"""
    try:
        # Extrair chave do corpo da requisição
        body = await request.json()
        chave = body.get("chave", "").strip().upper()
        
        logger.info(f"🔑 Validação de chave recebida: {chave[:4]}****")  # Log parcial por segurança
        
        # Validar formato da chave (8 caracteres)
        if not chave or len(chave) != 8:
            return {"sucesso": False, "mensagem": "Chave inválida. Use 8 caracteres."}
        
        # Conectar ao banco de dados
        conn = sqlite3.connect("acessos.db")
        cursor = conn.cursor()
        
        # Garantir que as tabelas existem
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                key TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used INTEGER DEFAULT 0,
                ip TEXT,
                user_agent TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS acessos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                chave_utilizada TEXT,
                data_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip TEXT,
                user_agent TEXT
            )
        ''')
        
        # Buscar chave no banco
        cursor.execute('''
            SELECT id, email, created_at, expires_at 
            FROM access_keys 
            WHERE key = ?
        ''', (chave,))
        
        resultado = cursor.fetchone()
        
        # Chave não encontrada
        if not resultado:
            conn.close()
            logger.warning(f"❌ Chave inválida tentada: {chave[:4]}****")
            return {"sucesso": False, "mensagem": "Chave inválida!"}
        
        # Extrair dados da chave
        id_solicitacao, email, created_at_str, expires_at_str = resultado
        created_at = datetime.fromisoformat(created_at_str)
        expires_at = datetime.fromisoformat(expires_at_str)
        now = datetime.now()
        
        # Verificar se a chave expirou
        if now > expires_at:
            horas_passadas = (now - expires_at).total_seconds() / 3600
            conn.close()
            logger.info(f"⏰ Chave expirada: {email} - {chave[:4]}****")
            return {
                "sucesso": False, 
                "mensagem": f"Chave expirada há {horas_passadas:.1f} horas! Solicite uma nova."
            }
        
        # Verificar se a chave ainda não está ativa (caso raro)
        if now < created_at:
            conn.close()
            return {"sucesso": False, "mensagem": "Chave ainda não está ativa!"}
        
        # IMPORTANTE: A chave NÃO é marcada como usada
        # Isso permite que o usuário reutilize a mesma chave dentro do período de 4 horas
        # Esta é uma boa prática de UX e reduz carga no banco de dados
        
        # Registrar o acesso para fins estatísticos
        ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        cursor.execute('''
            INSERT INTO acessos (email, chave_utilizada, ip, user_agent)
            VALUES (?, ?, ?, ?)
        ''', (email, chave, ip, user_agent))
        
        conn.commit()
        conn.close()
        
        # Calcular horas restantes de validade
        horas_restantes = (expires_at - now).total_seconds() / 3600
        
        logger.info(f"✅ Acesso liberado: {email} - Chave válida por mais {horas_restantes:.1f}h")
        
        return {
            "sucesso": True,
            "mensagem": f"✅ Acesso liberado! Chave válida por mais {horas_restantes:.1f} horas.",
            "email": email,
            "expira_em": expires_at.isoformat(),
            "horas_restantes": horas_restantes
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao validar chave: {e}")
        return {"sucesso": False, "mensagem": f"Erro interno. Tente novamente."}

""" Endpoint para verificar se a API está funcionando. """
@router.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "timestamp": datetime.now().isoformat(),
        "service": "InvestSmart API",
        "environment": ENVIRONMENT
    }

""" Endpoint simples para teste de conectividade. """
@router.get("/ping")
async def ping():
    return {
        "pong": True, 
        "time": datetime.now().isoformat()
    }