"""Repositório unificado para dados administrativos"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class UnifiedAdminRepository:
    """Repositório unificado que usa a tabela access_keys"""
    
    def __init__(self, db_path: str = "acessos.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Garante que a tabela access_keys existe"""
        with sqlite3.connect(self.db_path) as conn:
            # Garantir que a tabela access_keys existe
            conn.execute('''
                CREATE TABLE IF NOT EXISTS access_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    key TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    ip TEXT,
                    user_agent TEXT
                )
            ''')
            
            # Criar tabela de acessos se não existir
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
            
            # Índices
            conn.execute('CREATE INDEX IF NOT EXISTS idx_access_keys_email ON access_keys(email)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_access_keys_created ON access_keys(created_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_acessos_email ON acessos(email)')
            
            logger.info("✅ Tabelas unificadas verificadas")
    
    def get_solicitacoes(self, limite: int = 100, offset: int = 0) -> List[Dict]:
        """Retorna solicitações de chave da tabela access_keys"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT 
                    id,
                    email,
                    key as chave,
                    created_at as data_solicitacao,
                    expires_at as data_expiracao,
                    used as usado,
                    ip,
                    user_agent,
                    CASE 
                        WHEN used = 1 THEN 'usada'
                        WHEN datetime(expires_at) < datetime('now') THEN 'expirada'
                        ELSE 'ativa'
                    END as status,
                    CASE 
                        WHEN used = 1 THEN '✅ Usada'
                        WHEN datetime(expires_at) < datetime('now') THEN '⏰ Expirada'
                        ELSE '🕐 Ativa'
                    END as status_icone
                FROM access_keys
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (limite, offset))
            
            results = [dict(row) for row in cursor.fetchall()]
            logger.info(f"📋 Encontradas {len(results)} solicitações na tabela access_keys")
            return results
    
    def get_acessos(self, limite: int = 100, offset: int = 0) -> List[Dict]:
        """Retorna acessos reais ao dashboard"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT 
                    a.id,
                    a.email,
                    a.chave_utilizada,
                    a.data_acesso,
                    a.ip,
                    a.user_agent,
                    ak.created_at as chave_gerada_em
                FROM acessos a
                LEFT JOIN access_keys ak ON a.chave_utilizada = ak.key
                ORDER BY a.data_acesso DESC
                LIMIT ? OFFSET ?
            ''', (limite, offset))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_estatisticas(self) -> Dict:
        """Retorna estatísticas reais do sistema"""
        with sqlite3.connect(self.db_path) as conn:
            # Total de solicitações
            total_solicitacoes = conn.execute('SELECT COUNT(*) FROM access_keys').fetchone()[0]
            
            # Solicitações hoje
            hoje = datetime.now().strftime('%Y-%m-%d')
            solicitacoes_hoje = conn.execute(
                'SELECT COUNT(*) FROM access_keys WHERE date(created_at) = ?',
                (hoje,)
            ).fetchone()[0]
            
            # Total de acessos
            total_acessos = conn.execute('SELECT COUNT(*) FROM acessos').fetchone()[0]
            
            # Acessos hoje
            acessos_hoje = conn.execute(
                'SELECT COUNT(*) FROM acessos WHERE date(data_acesso) = ?',
                (hoje,)
            ).fetchone()[0]
            
            # Emails únicos
            emails_unicos = conn.execute('SELECT COUNT(DISTINCT email) FROM access_keys').fetchone()[0]
            
            # Taxa de conversão (solicitações que viraram acesso)
            conversao = conn.execute('''
                SELECT 
                    COUNT(DISTINCT a.email) * 100.0 / COUNT(DISTINCT ak.email)
                FROM access_keys ak
                LEFT JOIN acessos a ON ak.email = a.email
            ''').fetchone()[0] or 0
            
            # Solicitações por dia (últimos 7 dias)
            sete_dias_atras = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            solicitacoes_por_dia = conn.execute('''
                SELECT 
                    date(created_at) as dia,
                    COUNT(*) as total
                FROM access_keys
                WHERE date(created_at) >= ?
                GROUP BY date(created_at)
                ORDER BY dia DESC
            ''', (sete_dias_atras,)).fetchall()
            
            return {
                "total_solicitacoes": total_solicitacoes,
                "solicitacoes_hoje": solicitacoes_hoje,
                "total_acessos": total_acessos,
                "acessos_hoje": acessos_hoje,
                "emails_unicos": emails_unicos,
                "taxa_conversao": round(conversao, 2),
                "solicitacoes_por_dia": [
                    {"dia": row[0], "total": row[1]} for row in solicitacoes_por_dia
                ]
            }
    
    def get_ultimas_atividades(self, limite: int = 20) -> List[Dict]:
        """Retorna as últimas atividades"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT 
                    'solicitacao' as tipo,
                    email,
                    created_at as data,
                    key as identificador,
                    CASE WHEN used = 1 THEN 'usada' ELSE 'pendente' END as status
                FROM access_keys
                
                UNION ALL
                
                SELECT 
                    'acesso' as tipo,
                    a.email,
                    a.data_acesso as data,
                    a.chave_utilizada as identificador,
                    'sucesso' as status
                FROM acessos a
                
                ORDER BY data DESC
                LIMIT ?
            ''', (limite,))
            
            return [dict(row) for row in cursor.fetchall()]

# Instância global
admin_repo = UnifiedAdminRepository()