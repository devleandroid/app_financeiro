# Repositório para dados administrativos"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AdminRepository:
    """Repositório para consultas administrativas"""
    
    def __init__(self, db_path: str = "acessos.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Inicializa as tabelas necessárias"""
        with sqlite3.connect(self.db_path) as conn:
            # Tabela de solicitações de chave
            conn.execute('''
                CREATE TABLE IF NOT EXISTS solicitacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    chave TEXT UNIQUE NOT NULL,
                    data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_expiracao TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'pendente',
                    ip TEXT,
                    user_agent TEXT
                )
            ''')
            
            # Tabela de acessos
            conn.execute('''
                CREATE TABLE IF NOT EXISTS acessos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    chave_utilizada TEXT,
                    data_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip TEXT,
                    user_agent TEXT,
                    sucesso BOOLEAN DEFAULT 1
                )
            ''')
            
            # Índices para performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_solicitacoes_email ON solicitacoes(email)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_solicitacoes_data ON solicitacoes(data_solicitacao)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_acessos_email ON acessos(email)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_acessos_data ON acessos(data_acesso)')
            
            logger.info("✅ Tabelas administrativas criadas/verificadas")
    
    def get_solicitacoes(self, limite: int = 100, offset: int = 0) -> List[Dict]:
        """Retorna solicitações de chave reais"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT 
                    id,
                    email,
                    chave,
                    data_solicitacao,
                    data_expiracao,
                    status,
                    ip,
                    
                    CASE 
                        WHEN datetime(data_expiracao) < datetime('now') THEN 'expirada'
                        WHEN status = 'usada' THEN 'usada'
                        ELSE 'ativa'
                    END as status_atual,
                    
                    CASE 
                        WHEN status = 'usada' THEN '✅ Usada'
                        WHEN datetime(data_expiracao) < datetime('now') THEN '⏰ Expirada'
                        ELSE '🕐 Ativa'
                    END as status_icone
                    
                FROM solicitacoes
                ORDER BY data_solicitacao DESC
                LIMIT ? OFFSET ?
            ''', (limite, offset))
            
            return [dict(row) for row in cursor.fetchall()]
    
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
                    s.data_solicitacao as chave_gerada_em,
                    strftime('%s', a.data_acesso) - strftime('%s', s.data_solicitacao) as tempo_para_usar_segundos
                FROM acessos a
                LEFT JOIN solicitacoes s ON a.chave_utilizada = s.chave
                ORDER BY a.data_acesso DESC
                LIMIT ? OFFSET ?
            ''', (limite, offset))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_estatisticas(self) -> Dict:
        """Retorna estatísticas reais do sistema"""
        with sqlite3.connect(self.db_path) as conn:
            # Total de solicitações
            total_solicitacoes = conn.execute('SELECT COUNT(*) FROM solicitacoes').fetchone()[0]
            
            # Solicitações hoje
            hoje = datetime.now().strftime('%Y-%m-%d')
            solicitacoes_hoje = conn.execute(
                'SELECT COUNT(*) FROM solicitacoes WHERE date(data_solicitacao) = ?',
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
            emails_unicos = conn.execute('SELECT COUNT(DISTINCT email) FROM solicitacoes').fetchone()[0]
            
            # Taxa de conversão (solicitações que viraram acesso)
            conversao = conn.execute('''
                SELECT 
                    COUNT(DISTINCT a.email) * 100.0 / COUNT(DISTINCT s.email)
                FROM solicitacoes s
                LEFT JOIN acessos a ON s.email = a.email
            ''').fetchone()[0] or 0
            
            # Solicitações por dia (últimos 7 dias)
            sete_dias_atras = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            solicitacoes_por_dia = conn.execute('''
                SELECT 
                    date(data_solicitacao) as dia,
                    COUNT(*) as total
                FROM solicitacoes
                WHERE date(data_solicitacao) >= ?
                GROUP BY date(data_solicitacao)
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
        """Retorna as últimas atividades (solicitações + acessos)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT 
                    'solicitacao' as tipo,
                    email,
                    data_solicitacao as data,
                    chave as identificador,
                    status
                FROM solicitacoes
                
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
admin_repo = AdminRepository()