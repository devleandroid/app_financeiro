# database.py - VERSÃO CORRIGIDA
import sqlite3
import datetime
import random
import string
import secrets
from typing import Optional, Tuple
import pandas as pd

class Database:
    def __init__(self, db_path="acessos.db"):
        self.db_path = db_path
        self.criar_tabelas()
    
    def criar_tabelas(self):
        """Cria as tabelas com a estrutura correta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de solicitações de chave
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solicitacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                chave TEXT UNIQUE NOT NULL,
                data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_expiracao TIMESTAMP NOT NULL,
                usado BOOLEAN DEFAULT 0,
                ip TEXT,
                user_agent TEXT
            )
        ''')
        
        # Tabela de acessos - com a coluna chave_utilizada
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS acessos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                chave_utilizada TEXT,
                data_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip TEXT,
                user_agent TEXT,
                FOREIGN KEY (chave_utilizada) REFERENCES solicitacoes(chave)
            )
        ''')
        
        # Índices para busca rápida
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chave ON solicitacoes(chave)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email_solicitacoes ON solicitacoes(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email_acessos ON acessos(email)')
        
        conn.commit()
        conn.close()
        print("✅ Banco de dados configurado corretamente!")
    
    def solicitar_chave(self, email: str, ip: str = None, user_agent: str = None) -> Tuple[bool, str, Optional[str]]:
        """Gera uma nova chave para o email"""
        try:
            email = email.lower().strip()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se já existe chave válida não expirada
            cursor.execute('''
                SELECT chave FROM solicitacoes 
                WHERE email = ? AND usado = 0 AND datetime(data_expiracao) > datetime('now')
                ORDER BY data_expiracao DESC LIMIT 1
            ''', (email,))
            
            chave_existente = cursor.fetchone()
            
            if chave_existente:
                conn.close()
                return False, "Você já possui uma chave válida. Verifique seu email.", chave_existente[0]
            
            # Gerar nova chave
            caracteres = string.ascii_uppercase + string.digits
            chave = ''.join(secrets.choice(caracteres) for _ in range(8))
            
            # Calcular expiração (4 horas)
            data_expiracao = datetime.datetime.now() + datetime.timedelta(hours=4)
            
            cursor.execute('''
                INSERT INTO solicitacoes (email, chave, data_expiracao, ip, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, chave, data_expiracao.isoformat(), ip, user_agent))
            
            conn.commit()
            conn.close()
            
            return True, "Chave gerada com sucesso!", chave
            
        except Exception as e:
            print(f"Erro ao gerar chave: {e}")
            return False, f"Erro interno: {str(e)}", None
    
    def validar_chave(self, chave: str, ip: str = None, user_agent: str = None) -> Tuple[bool, str, Optional[str]]:
        """Valida uma chave e registra o acesso"""
        try:
            chave = chave.upper().strip()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar chave
            cursor.execute('''
                SELECT id, email, data_expiracao, usado 
                FROM solicitacoes 
                WHERE chave = ?
            ''', (chave,))
            
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                return False, "Chave inválida! Verifique o código digitado.", None
            
            id_solicitacao, email, data_expiracao_str, usado = resultado
            
            # Verificar expiração
            data_expiracao = datetime.datetime.fromisoformat(data_expiracao_str)
            if datetime.datetime.now() > data_expiracao:
                conn.close()
                return False, "Chave expirada! Solicite uma nova chave.", None
            
            # Verificar se já foi usada
            if usado:
                conn.close()
                return False, "Chave já utilizada! Solicite uma nova chave.", None
            
            # Marcar como usada
            cursor.execute('UPDATE solicitacoes SET usado = 1 WHERE id = ?', (id_solicitacao,))
            
            # Registrar acesso - AGORA COM A COLUNA CORRETA
            cursor.execute('''
                INSERT INTO acessos (email, chave_utilizada, ip, user_agent)
                VALUES (?, ?, ?, ?)
            ''', (email, chave, ip, user_agent))
            
            conn.commit()
            conn.close()
            
            return True, "Chave válida! Acesso liberado.", email
            
        except sqlite3.OperationalError as e:
            print(f"Erro no banco de dados: {e}")
            return False, "Erro na estrutura do banco de dados. Execute o script de correção.", None
        except Exception as e:
            print(f"Erro ao validar chave: {e}")
            return False, f"Erro interno: {str(e)}", None
    
    def listar_todas_solicitacoes(self) -> pd.DataFrame:
        """Lista todas as solicitações"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT 
                id, email, chave, data_solicitacao, data_expiracao, usado, ip
            FROM solicitacoes 
            ORDER BY data_solicitacao DESC
        ''', conn)
        conn.close()
        return df
    
    def listar_todos_acessos(self) -> pd.DataFrame:
        """Lista todos os acessos"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT 
                a.id, a.email, a.chave_utilizada, a.data_acesso, a.ip,
                s.data_solicitacao
            FROM acessos a
            LEFT JOIN solicitacoes s ON a.chave_utilizada = s.chave
            ORDER BY a.data_acesso DESC
        ''', conn)
        conn.close()
        return df

# Instância global
db = Database()