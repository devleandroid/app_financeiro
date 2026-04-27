"""
Migracao para criar as tabelas da plataforma de criacao de sites.

Tabelas criadas:
- users: Usuarios da plataforma (cadastro, login, plano)
- sites: Sites criados pelos usuarios
- subscriptions: Assinaturas dos planos
- payments: Pagamentos realizados
"""
import sqlite3
import os
from pathlib import Path


def get_db_path():
    """Retorna o caminho do banco de dados."""
    base_dir = Path(__file__).parent.parent.parent.parent.parent
    return str(base_dir / "sites_platform.db")


def criar_tabelas(db_path: str = None):
    """Cria todas as tabelas necessarias para a plataforma de sites."""
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tabela de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nome TEXT NOT NULL,
            telefone TEXT,
            plano TEXT DEFAULT 'free',
            sites_criados INTEGER DEFAULT 0,
            ativo BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de sites
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nome_negocio TEXT NOT NULL,
            descricao TEXT,
            segmento TEXT,
            telefone TEXT,
            whatsapp TEXT,
            email_contato TEXT,
            endereco TEXT,
            template_id TEXT NOT NULL,
            cor_primaria TEXT DEFAULT '#2563eb',
            cor_secundaria TEXT DEFAULT '#1e1e2e',
            cor_texto TEXT DEFAULT '#ffffff',
            logo_url TEXT,
            fotos TEXT,
            redes_sociais TEXT,
            slug TEXT UNIQUE,
            status TEXT DEFAULT 'rascunho',
            html_gerado TEXT,
            site_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Tabela de assinaturas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plano TEXT NOT NULL DEFAULT 'pro',
            valor REAL DEFAULT 69.90,
            status TEXT DEFAULT 'active',
            payment_gateway TEXT,
            external_subscription_id TEXT,
            inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fim TIMESTAMP,
            proximo_pagamento TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Tabela de pagamentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            descricao TEXT,
            status TEXT DEFAULT 'pending',
            payment_gateway TEXT,
            external_payment_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Tabela de templates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            descricao TEXT,
            categoria TEXT,
            thumbnail_url TEXT,
            ativo BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Indices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sites_user_id ON sites(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sites_slug ON sites(slug)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sites_status ON sites(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)')

    # Inserir templates padrao
    templates_padrao = [
        ("restaurante", "Restaurante & Gastronomia",
         "Landing page profissional para restaurantes, bares e lanchonetes",
         "gastronomia", "/static/img/template_restaurante.jpg"),
        ("loja", "Loja & Comercio",
         "Landing page para lojas, boutiques e comercio em geral",
         "comercio", "/static/img/template_loja.jpg"),
        ("portfolio", "Portfolio & Servicos",
         "Landing page para profissionais liberais, freelancers e portfolios",
         "servicos", "/static/img/template_portfolio.jpg"),
        ("saude", "Saude & Bem-estar",
         "Landing page para clinicas, consultorios e profissionais de saude",
         "saude", "/static/img/template_saude.jpg"),
    ]

    for t in templates_padrao:
        cursor.execute('''
            INSERT OR IGNORE INTO templates (id, nome, descricao, categoria, thumbnail_url)
            VALUES (?, ?, ?, ?, ?)
        ''', t)

    conn.commit()
    conn.close()
    print("Tabelas da plataforma de sites criadas com sucesso!")
    print(f"Banco de dados: {db_path}")


if __name__ == "__main__":
    criar_tabelas()
