"""Repositório unificado para dados - Suporta SQLite e PostgreSQL"""
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Verificar qual banco usar
DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL and "postgres" in DATABASE_URL:
    # Usar PostgreSQL
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2.pool import SimpleConnectionPool
    
    class UnifiedAdminRepository:
        def __init__(self):
            self.db_url = DATABASE_URL
            # Criar pool de conexões (melhor performance)
            self.pool = SimpleConnectionPool(1, 5, self.db_url)
            self._init_db()
        
        def _get_connection(self):
            return self.pool.getconn()
        
        def _return_connection(self, conn):
            self.pool.putconn(conn)
        
        def _init_db(self):
            """Cria as tabelas no PostgreSQL se não existirem"""
            conn = self._get_connection()
            try:
                with conn.cursor() as cur:
                    # Tabela de chaves de acesso
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
                    
                    # Tabela de acessos
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
                    
                    # Índices para melhor performance
                    cur.execute('CREATE INDEX IF NOT EXISTS idx_access_keys_email ON access_keys(email)')
                    cur.execute('CREATE INDEX IF NOT EXISTS idx_access_keys_key ON access_keys(key)')
                    cur.execute('CREATE INDEX IF NOT EXISTS idx_acessos_email ON acessos(email)')
                    cur.execute('CREATE INDEX IF NOT EXISTS idx_acessos_chave ON acessos(chave_utilizada)')
                    
                    conn.commit()
                    logger.info("✅ Tabelas PostgreSQL criadas/verificadas com sucesso")
            except Exception as e:
                logger.error(f"❌ Erro ao criar tabelas: {e}")
                raise
            finally:
                self._return_connection(conn)
        
        def get_solicitacoes(self, limite: int = 100, offset: int = 0) -> List[Dict]:
            """Retorna solicitações de chave"""
            conn = self._get_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute('''
                        SELECT 
                            id,
                            email,
                            key as chave,
                            created_at as data_solicitacao,
                            expires_at as data_expiracao,
                            used,
                            ip,
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
                self._return_connection(conn)
        
        def get_acessos(self, limite: int = 100, offset: int = 0) -> List[Dict]:
            """Retorna acessos ao dashboard"""
            conn = self._get_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute('''
                        SELECT 
                            a.id,
                            a.email,
                            a.chave_utilizada,
                            a.data_acesso,
                            a.ip,
                            ak.created_at as chave_gerada_em
                        FROM acessos a
                        LEFT JOIN access_keys ak ON a.chave_utilizada = ak.key
                        ORDER BY a.data_acesso DESC
                        LIMIT %s OFFSET %s
                    ''', (limite, offset))
                    
                    return [dict(row) for row in cur.fetchall()]
            finally:
                self._return_connection(conn)
        
        def get_estatisticas(self) -> Dict:
            """Retorna estatísticas do sistema"""
            conn = self._get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute('SELECT COUNT(*) FROM access_keys')
                    total_solicitacoes = cur.fetchone()[0]
                    
                    cur.execute('SELECT COUNT(*) FROM acessos')
                    total_acessos = cur.fetchone()[0]
                    
                    cur.execute('SELECT COUNT(DISTINCT email) FROM access_keys')
                    emails_unicos = cur.fetchone()[0]
                    
                    # Calcular taxa de conversão
                    if total_solicitacoes > 0:
                        taxa_conversao = round((total_acessos / total_solicitacoes) * 100, 2)
                    else:
                        taxa_conversao = 0
                    
                    # Solicitações hoje
                    cur.execute('''
                        SELECT COUNT(*) FROM access_keys 
                        WHERE DATE(created_at) = CURRENT_DATE
                    ''')
                    solicitacoes_hoje = cur.fetchone()[0]
                    
                    # Acessos hoje
                    cur.execute('''
                        SELECT COUNT(*) FROM acessos 
                        WHERE DATE(data_acesso) = CURRENT_DATE
                    ''')
                    acessos_hoje = cur.fetchone()[0]
                    
                    return {
                        "total_solicitacoes": total_solicitacoes,
                        "solicitacoes_hoje": solicitacoes_hoje,
                        "total_acessos": total_acessos,
                        "acessos_hoje": acessos_hoje,
                        "emails_unicos": emails_unicos,
                        "taxa_conversao": taxa_conversao,
                        "solicitacoes_por_dia": []
                    }
            finally:
                self._return_connection(conn)
        
        def registrar_solicitacao(self, email: str, chave: str, ip: str = None) -> bool:
            """Registra uma nova solicitação de chave"""
            conn = self._get_connection()
            try:
                from datetime import datetime, timedelta
                now = datetime.now()
                expires_at = now + timedelta(hours=4)
                
                with conn.cursor() as cur:
                    cur.execute('''
                        INSERT INTO access_keys (email, key, created_at, expires_at, used, ip)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (email, chave, now, expires_at, 0, ip))
                    conn.commit()
                    return True
            except Exception as e:
                logger.error(f"Erro ao registrar solicitação: {e}")
                return False
            finally:
                self._return_connection(conn)
        
        def registrar_acesso(self, email: str, chave: str, ip: str = None) -> bool:
            """Registra um acesso ao sistema"""
            conn = self._get_connection()
            try:
                with conn.cursor() as cur:
                    # Marcar chave como usada
                    cur.execute('UPDATE access_keys SET used = 1 WHERE key = %s', (chave,))
                    # Registrar acesso
                    cur.execute('''
                        INSERT INTO acessos (email, chave_utilizada, ip)
                        VALUES (%s, %s, %s)
                    ''', (email, chave, ip))
                    conn.commit()
                    return True
            except Exception as e:
                logger.error(f"Erro ao registrar acesso: {e}")
                return False
            finally:
                self._return_connection(conn)

else:
    # Usar SQLite (fallback para desenvolvimento)
    import sqlite3
    
    class UnifiedAdminRepository:
        def __init__(self, db_path: str = "acessos.db"):
            self.db_path = db_path
            self._init_db()
            logger.info("📁 Usando SQLite local para desenvolvimento")
        
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
        
        def registrar_solicitacao(self, email: str, chave: str, ip: str = None) -> bool:
            from datetime import datetime, timedelta
            now = datetime.now()
            expires_at = now + timedelta(hours=4)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO access_keys (email, key, created_at, expires_at, used, ip)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (email, chave, now.isoformat(), expires_at.isoformat(), 0, ip))
                conn.commit()
                return True
        
        def registrar_acesso(self, email: str, chave: str, ip: str = None) -> bool:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE access_keys SET used = 1 WHERE key = ?', (chave,))
                cursor.execute('''
                    INSERT INTO acessos (email, chave_utilizada, ip)
                    VALUES (?, ?, ?)
                ''', (email, chave, ip))
                conn.commit()
                return True

# Instância global
admin_repo = UnifiedAdminRepository()
