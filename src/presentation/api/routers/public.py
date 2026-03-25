"""Rotas públicas da API"""
from fastapi import APIRouter, Request
from datetime import datetime, timedelta
import logging
import string
import secrets
import sqlite3

# Importar do arquivo correto (email_smtp.py)
from src.infrastructure.external.email_smtp import EmailSender

logger = logging.getLogger(__name__)
router = APIRouter(tags=["public"])

# Criar instância do serviço de email
email_sender = EmailSender()

def gerar_chave():
    """Gera uma chave aleatória de 8 caracteres"""
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(8))

def salvar_solicitacao(email, chave, ip=None):
    """Salva a solicitação no banco de dados"""
    conn = sqlite3.connect("acessos.db")
    cursor = conn.cursor()
    
    # Garantir que a tabela existe
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
    
    # Calcular expiração (4 horas)
    now = datetime.now()
    expires_at = now + timedelta(hours=4)
    
    cursor.execute('''
        INSERT INTO access_keys (email, key, created_at, expires_at, used, ip)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (email, chave, now.isoformat(), expires_at.isoformat(), 0, ip))
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Solicitação salva: {email} -> {chave}")

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
        
        # Verificar se já existe chave válida
        conn = sqlite3.connect("acessos.db")
        cursor = conn.cursor()
        
        # Garantir tabela existe
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
            SELECT key FROM access_keys 
            WHERE email = ? AND used = 0 AND datetime(expires_at) > datetime('now')
        ''', (email,))
        existing = cursor.fetchone()
        conn.close()
        
        if existing:
            return {
                "sucesso": False,
                "mensagem": "Você já possui uma chave válida. Verifique seu email."
            }
        
        # Gerar nova chave
        chave = gerar_chave()
        
        # Salvar no banco
        ip = request.client.host if request.client else None
        salvar_solicitacao(email, chave, ip)
        
        # ENVIAR EMAIL usando o EmailSender existente
        email_enviado = email_sender.send_key(email, chave)
        
        if email_enviado:
            mensagem = f"Chave enviada para {email}! Válida por 4 horas."
        else:
            mensagem = f"Chave gerada: {chave} (falha no email - use esta chave)"
        
        logger.info(f"✅ Chave gerada: {chave} para {email}")
        
        return {
            "sucesso": True,
            "mensagem": mensagem,
            "chave": chave if not email_enviado else None
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
        
        conn = sqlite3.connect("acessos.db")
        cursor = conn.cursor()
        
        # Garantir tabelas existem
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
        
        # Buscar chave
        cursor.execute('''
            SELECT id, email, expires_at, used 
            FROM access_keys 
            WHERE key = ?
        ''', (chave,))
        
        resultado = cursor.fetchone()
        
        if not resultado:
            conn.close()
            return {"sucesso": False, "mensagem": "Chave inválida!"}
        
        id_solicitacao, email, expires_at_str, usado = resultado
        expires_at = datetime.fromisoformat(expires_at_str)
        
        # Verificar expiração
        if datetime.now() > expires_at:
            conn.close()
            return {"sucesso": False, "mensagem": "Chave expirada! Solicite uma nova."}
        
        # Verificar se já foi usada
        if usado:
            conn.close()
            return {"sucesso": False, "mensagem": "Chave já utilizada!"}
        
        # Marcar como usada
        cursor.execute('UPDATE access_keys SET used = 1 WHERE id = ?', (id_solicitacao,))
        
        # Registrar acesso
        ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        cursor.execute('''
            INSERT INTO acessos (email, chave_utilizada, ip, user_agent)
            VALUES (?, ?, ?, ?)
        ''', (email, chave, ip, user_agent))
        
        conn.commit()
        conn.close()
        
        return {
            "sucesso": True,
            "mensagem": "Acesso liberado!",
            "email": email
        }
        
    except Exception as e:
        logger.error(f"Erro ao validar chave: {e}")
        return {"sucesso": False, "mensagem": f"Erro: {str(e)}"}