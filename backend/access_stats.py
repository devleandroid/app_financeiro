import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger('app')

class AccessStatsDB:
    """Banco de dados para estatísticas de acesso"""
    
    def __init__(self, db_path="access_stats.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Inicializa as tabelas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de acessos diários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_access (
                date TEXT PRIMARY KEY,
                total_requests INTEGER DEFAULT 0,
                unique_ips INTEGER DEFAULT 0,
                unique_users INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                status_2xx INTEGER DEFAULT 0,
                status_4xx INTEGER DEFAULT 0,
                status_5xx INTEGER DEFAULT 0,
                top_endpoints TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de acessos detalhados (para relatórios)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                method TEXT,
                path TEXT,
                status_code INTEGER,
                client_ip TEXT,
                user TEXT,
                user_agent TEXT,
                process_time REAL,
                date TEXT
            )
        ''')
        
        # Índices para consultas rápidas
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_date ON access_log(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_ip ON access_log(client_ip)')
        
        conn.commit()
        conn.close()
        logger.info("Banco de dados de estatísticas inicializado")
    
    def log_access(self, method: str, path: str, status_code: int, 
                   client_ip: str, user: Optional[str], user_agent: str, 
                   process_time: float):
        """Registra um acesso no banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute('''
                INSERT INTO access_log 
                (method, path, status_code, client_ip, user, user_agent, process_time, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (method, path, status_code, client_ip, user, user_agent, process_time, today))
            
            conn.commit()
            conn.close()
            
            # Atualizar estatísticas diárias em background (pode ser feito depois)
            
        except Exception as e:
            logger.error(f"Erro ao registrar acesso: {e}")
    
    def update_daily_stats(self, date: Optional[str] = None):
        """Atualiza estatísticas do dia"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de requisições
        cursor.execute('''
            SELECT COUNT(*) FROM access_log WHERE date = ?
        ''', (date,))
        total = cursor.fetchone()[0]
        
        # IPs únicos
        cursor.execute('''
            SELECT COUNT(DISTINCT client_ip) FROM access_log WHERE date = ?
        ''', (date,))
        unique_ips = cursor.fetchone()[0]
        
        # Usuários únicos (não nulos)
        cursor.execute('''
            SELECT COUNT(DISTINCT user) FROM access_log 
            WHERE date = ? AND user IS NOT NULL
        ''', (date,))
        unique_users = cursor.fetchone()[0]
        
        # Tempo médio de resposta
        cursor.execute('''
            SELECT AVG(process_time) FROM access_log WHERE date = ?
        ''', (date,))
        avg_time = cursor.fetchone()[0] or 0
        
        # Status codes
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN status_code >= 200 AND status_code < 300 THEN 1 ELSE 0 END) as s2xx,
                SUM(CASE WHEN status_code >= 400 AND status_code < 500 THEN 1 ELSE 0 END) as s4xx,
                SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) as s5xx
            FROM access_log WHERE date = ?
        ''', (date,))
        s2xx, s4xx, s5xx = cursor.fetchone()
        
        # Top endpoints
        cursor.execute('''
            SELECT path, COUNT(*) as count 
            FROM access_log 
            WHERE date = ?
            GROUP BY path
            ORDER BY count DESC
            LIMIT 5
        ''', (date,))
        top_endpoints = cursor.fetchall()
        
        # Inserir ou atualizar
        cursor.execute('''
            INSERT OR REPLACE INTO daily_access 
            (date, total_requests, unique_ips, unique_users, avg_response_time,
             status_2xx, status_4xx, status_5xx, top_endpoints)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, total, unique_ips, unique_users, avg_time, 
              s2xx or 0, s4xx or 0, s5xx or 0, json.dumps(top_endpoints)))
        
        conn.commit()
        conn.close()
        logger.info(f"Estatísticas diárias atualizadas para {date}")
    
    def get_weekly_report(self) -> Dict:
        """Gera relatório da última semana"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Últimos 7 dias
        cursor.execute('''
            SELECT * FROM daily_access
            WHERE date >= date('now', '-7 days')
            ORDER BY date DESC
        ''')
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        daily_stats = []
        for row in rows:
            daily = dict(zip(columns, row))
            daily['top_endpoints'] = json.loads(daily['top_endpoints'])
            daily_stats.append(daily)
        
        # Totais da semana
        cursor.execute('''
            SELECT 
                SUM(total_requests) as week_total,
                AVG(avg_response_time) as week_avg_time,
                COUNT(DISTINCT date) as days_with_data
            FROM daily_access
            WHERE date >= date('now', '-7 days')
        ''')
        totals = cursor.fetchone()
        
        conn.close()
        
        return {
            "period": "last_7_days",
            "generated_at": datetime.now().isoformat(),
            "daily_stats": daily_stats,
            "summary": {
                "total_requests": totals[0] or 0,
                "avg_response_time": round(totals[1] or 0, 3),
                "days_with_data": totals[2] or 0
            }
        }

# Instância global
stats_db = AccessStatsDB()
