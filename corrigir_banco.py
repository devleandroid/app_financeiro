# corrigir_banco.py
import sqlite3

print("🔄 Corrigindo banco de dados...")

conn = sqlite3.connect("acessos.db")
cursor = conn.cursor()

# Verificar estrutura atual
cursor.execute("PRAGMA table_info(acessos)")
colunas = cursor.fetchall()
print("📊 Estrutura atual da tabela acessos:")
for col in colunas:
    print(f"   - {col[1]} ({col[2]})")

# Verificar se a coluna chave_utilizada existe
coluna_existe = any(col[1] == 'chave_utilizada' for col in colunas)

if not coluna_existe:
    print("🔄 Adicionando coluna chave_utilizada...")
    
    # Renomear tabela antiga
    cursor.execute("ALTER TABLE acessos RENAME TO acessos_antiga")
    
    # Criar nova tabela com a estrutura correta
    cursor.execute('''
        CREATE TABLE acessos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            chave_utilizada TEXT,
            data_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip TEXT,
            user_agent TEXT
        )
    ''')
    
    # Copiar dados da tabela antiga (adaptando conforme necessário)
    cursor.execute('''
        INSERT INTO acessos (id, email, data_acesso, ip, user_agent)
        SELECT id, email, data_acesso, ip, user_agent FROM acessos_antiga
    ''')
    
    # Remover tabela antiga
    cursor.execute("DROP TABLE acessos_antiga")
    
    print("✅ Coluna adicionada com sucesso!")
else:
    print("✅ Coluna chave_utilizada já existe!")

# Verificar estrutura da tabela solicitacoes
cursor.execute("PRAGMA table_info(solicitacoes)")
colunas_sol = cursor.fetchall()
print("\n📊 Estrutura da tabela solicitacoes:")
for col in colunas_sol:
    print(f"   - {col[1]} ({col[2]})")

conn.commit()
conn.close()

print("\n✅ Banco de dados corrigido!")
