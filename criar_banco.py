# criar_banco.py
import sqlite3

print("🔄 Recriando banco de dados...")

conn = sqlite3.connect("acessos.db")
cursor = conn.cursor()

# Criar tabela de solicitações
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

# Criar tabela de acessos com a coluna correta
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

# Índices
cursor.execute('CREATE INDEX IF NOT EXISTS idx_chave ON solicitacoes(chave)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_email_solicitacoes ON solicitacoes(email)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_email_acessos ON acessos(email)')

conn.commit()
conn.close()

print("✅ Banco de dados recriado com sucesso!")
print("📁 Arquivo: acessos.db")
