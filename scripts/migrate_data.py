#!/usr/bin/env python
"""Script para migrar dados da tabela solicitacoes para access_keys"""

import sqlite3
from datetime import datetime

DB_PATH = "acessos.db"

def migrate_data():
    """Migra dados da tabela solicitacoes para access_keys"""
    
    print("🔄 Migrando dados...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar se há dados na tabela solicitacoes
    cursor.execute("SELECT COUNT(*) FROM solicitacoes")
    count = cursor.fetchone()[0]
    print(f"📊 Encontradas {count} solicitações na tabela antiga")
    
    if count > 0:
        # Buscar dados da tabela antiga
        cursor.execute('''
            SELECT email, chave, data_solicitacao, data_expiracao, 
                   CASE WHEN status = 'usada' THEN 1 ELSE 0 END as usado, ip
            FROM solicitacoes
        ''')
        
        rows = cursor.fetchall()
        
        # Inserir na tabela access_keys
        for row in rows:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO access_keys 
                    (email, key, created_at, expires_at, used, ip, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (row[0], row[1], row[2], row[3], row[4], row[5], 'migrated'))
            except Exception as e:
                print(f"   ⚠️ Erro ao migrar {row[0]}: {e}")
        
        conn.commit()
        print(f"✅ {len(rows)} registros migrados com sucesso!")
    
    conn.close()
    print("✅ Migração concluída!")

if __name__ == "__main__":
    migrate_data()