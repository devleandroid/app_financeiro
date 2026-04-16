"""Repositório unificado para dados - Suporta SQLite e PostgreSQL"""
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Verificar ambiente
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Em desenvolvimento, sempre usar SQLite (a menos que explicitamente configurado)
if ENVIRONMENT == "development" and not DATABASE_URL:
    USE_POSTGRES = False
    logger.info("📁 Ambiente de desenvolvimento: usando SQLite")
else:
    USE_POSTGRES = DATABASE_URL and "postgres" in DATABASE_URL

if USE_POSTGRES:
    # Tentar usar PostgreSQL
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        PSYCOPG2_AVAILABLE = True
        logger.info("🐘 Conectando ao PostgreSQL em produção...")
    except ImportError:
        PSYCOPG2_AVAILABLE = False
        USE_POSTGRES = False
        logger.warning("⚠️ psycopg2 não disponível, usando SQLite")

if USE_POSTGRES and PSYCOPG2_AVAILABLE:
    # Usar PostgreSQL (produção)
    class UnifiedAdminRepository:
        def __init__(self):
            self.db_url = DATABASE_URL
            self._init_db()
        
        def _get_connection(self):
            return psycopg2.connect(self.db_url)
        
        def _init_db(self):
            """Cria as tabelas no PostgreSQL se não existirem"""
            conn = self._get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute('''
                        CREATE TABLE IF NOT EXISTS access_keys (
                            id SERIAL PRIMARY KEY,
                            email TEXT NOT NULL,
                            key TEXT UNIQUE NOT NULL,
                            created_at TIMESTAMP NOT NULL,
                            expires_at TIMESTAMP NOT NULL,
                            used INTEGER DEFAULT 0,
                            ip TEXT,
                            user_agent TEXT
                        )
                    ''')
                    
                    cur.execute('''
                        CREATE TABLE IF NOT EXISTS acessos (
                            id SERIAL PRIMARY KEY,
                            email TEXT NOT NULL,
                            chave_utilizada TEXT,
                            data_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            ip TEXT,
                            user_agent TEXT
                        )
                    ''')
                    
                    conn.commit()
                    logger.info("✅ Tabelas PostgreSQL criadas/verificadas")
            except Exception as e:
                logger.error(f"❌ Erro ao criar tabelas: {e}")
                raise
            finally:
                conn.close()
        
        def get_solicitacoes(self, limite: int = 100, offset: int = 0) -> List[Dict]:
            conn = self._get_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute('''
                        SELECT 
                            id, email, key as chave, created_at as data_solicitacao,
                            expires_at as data_expiracao, used, ip,
                            CASE 
                                WHEN used = 1 THEN 'usada'
                                WHEN expires_at < NOW() THEN 'expirada'
                                ELSE 'ativa'
                            END as status
                        FROM access_keys
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s
                    ''', (limite, offset))
                    
                    return [dict(row) for row in cur.fetchall()]
            finally:
                conn.close()
        
        def get_acessos(self, limite: int = 100, offset: int = 0) -> List[Dict]:
            conn = self._get_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute('''
                        SELECT a.id, a.email, a.chave_utilizada, a.data_acesso, a.ip,
                               ak.created_at as chave_gerada_em
                        FROM acessos a
                        LEFT JOIN access_keys ak ON a.chave_utilizada = ak.key
                        ORDER BY a.data_acesso DESC
                        LIMIT %s OFFSET %s
                    ''', (limite, offset))
                    
                    return [dict(row) for row in cur.fetchall()]
            finally:
                conn.close()
        
        def get_estatisticas(self) -> Dict:
            conn = self._get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute('SELECT COUNT(*) FROM access_keys')
                    total_solicitacoes = cur.fetchone()[0]
                    
                    cur.execute('SELECT COUNT(*) FROM acessos')
                    total_acessos = cur.fetchone()[0]
                    
                    cur.execute('SELECT COUNT(DISTINCT email) FROM access_keys')
                    emails_unicos = cur.fetchone()[0]
                    
                    return {
                        "total_solicitacoes": total_solicitacoes,
                        "solicitacoes_hoje": 0,
                        "total_acessos": total_acessos,
                        "acessos_hoje": 0,
                        "emails_unicos": emails_unicos,
                        "taxa_conversao": 0,
                        "solicitacoes_por_dia": []
                    }
            finally:
                conn.close()

else:
    # Usar SQLite (desenvolvimento)
    import sqlite3
    logger.info("📁 Usando SQLite local para desenvolvimento")
    
    class UnifiedAdminRepository:
        def __init__(self, db_path: str = "acessos.db"):
            self.db_path = db_path
            self._init_db()
        
        def _init_db(self):
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
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
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS acessos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL,
                        chave_utilizada TEXT,
                        data_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ip TEXT,
                        user_agent TEXT
                    )
                ''')
                
                logger.info("✅ Tabelas SQLite criadas/verificadas")
        
        def get_solicitacoes(self, limite: int = 100, offset: int = 0) -> List[Dict]:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT 
                        id, email, key as chave, created_at as data_solicitacao,
                        expires_at as data_expiracao, used, ip,
                        CASE 
                            WHEN used = 1 THEN 'usada'
                            WHEN datetime(expires_at) < datetime('now') THEN 'expirada'
                            ELSE 'ativa'
                        END as status
                    FROM access_keys
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                ''', (limite, offset))
                
                return [dict(row) for row in cursor.fetchall()]
        
        def get_acessos(self, limite: int = 100, offset: int = 0) -> List[Dict]:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT a.id, a.email, a.chave_utilizada, a.data_acesso, a.ip,
                           ak.created_at as chave_gerada_em
                    FROM acessos a
                    LEFT JOIN access_keys ak ON a.chave_utilizada = ak.key
                    ORDER BY a.data_acesso DESC
                    LIMIT ? OFFSET ?
                ''', (limite, offset))
                
                return [dict(row) for row in cursor.fetchall()]
        
        def get_estatisticas(self) -> Dict:
            with sqlite3.connect(self.db_path) as conn:
                total_solicitacoes = conn.execute('SELECT COUNT(*) FROM access_keys').fetchone()[0]
                total_acessos = conn.execute('SELECT COUNT(*) FROM acessos').fetchone()[0]
                emails_unicos = conn.execute('SELECT COUNT(DISTINCT email) FROM access_keys').fetchone()[0]
                
                return {
                    "total_solicitacoes": total_solicitacoes,
                    "solicitacoes_hoje": 0,
                    "total_acessos": total_acessos,
                    "acessos_hoje": 0,
                    "emails_unicos": emails_unicos,
                    "taxa_conversao": 0,
                    "solicitacoes_por_dia": []
                }

# Instância global
admin_repo = UnifiedAdminRepository()
