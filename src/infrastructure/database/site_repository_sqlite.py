"""Repositorio SQLite para a plataforma de sites."""
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def get_db_path() -> str:
    base_dir = Path(__file__).parent.parent.parent.parent
    return str(base_dir / "sites_platform.db")


def get_connection(db_path: str = None) -> sqlite3.Connection:
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ========== USERS ==========

def criar_usuario(email: str, password_hash: str, nome: str, telefone: str = None) -> dict:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, password_hash, nome, telefone) VALUES (?, ?, ?, ?)",
            (email, password_hash, nome, telefone)
        )
        conn.commit()
        return buscar_usuario_por_id(cursor.lastrowid)
    except sqlite3.IntegrityError:
        raise ValueError("Email ja cadastrado")
    finally:
        conn.close()


def buscar_usuario_por_email(email: str) -> Optional[dict]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def buscar_usuario_por_id(user_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def atualizar_plano_usuario(user_id: int, plano: str):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET plano = ?, updated_at = ? WHERE id = ?",
            (plano, datetime.now().isoformat(), user_id)
        )
        conn.commit()
    finally:
        conn.close()


def incrementar_sites_criados(user_id: int):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET sites_criados = sites_criados + 1, updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), user_id)
        )
        conn.commit()
    finally:
        conn.close()


def decrementar_sites_criados(user_id: int):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET sites_criados = MAX(0, sites_criados - 1), updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), user_id)
        )
        conn.commit()
    finally:
        conn.close()


def listar_todos_usuarios() -> list:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, nome, plano, sites_criados, ativo, created_at FROM users ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


# ========== SITES ==========

def criar_site(user_id: int, dados: dict) -> dict:
    conn = get_connection()
    try:
        fotos_json = json.dumps(dados.get("fotos", []))
        redes_json = json.dumps(dados.get("redes_sociais", {}))

        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sites (
                user_id, nome_negocio, descricao, segmento, telefone,
                whatsapp, email_contato, endereco, template_id,
                cor_primaria, cor_secundaria, cor_texto,
                logo_url, fotos, redes_sociais, slug, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            dados["nome_negocio"],
            dados.get("descricao", ""),
            dados.get("segmento", ""),
            dados.get("telefone", ""),
            dados.get("whatsapp", ""),
            dados.get("email_contato", ""),
            dados.get("endereco", ""),
            dados["template_id"],
            dados.get("cor_primaria", "#2563eb"),
            dados.get("cor_secundaria", "#1e1e2e"),
            dados.get("cor_texto", "#ffffff"),
            dados.get("logo_url", ""),
            fotos_json,
            redes_json,
            dados.get("slug"),
            "rascunho"
        ))
        conn.commit()
        incrementar_sites_criados(user_id)
        return buscar_site_por_id(cursor.lastrowid)
    finally:
        conn.close()


def buscar_site_por_id(site_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sites WHERE id = ?", (site_id,))
        row = cursor.fetchone()
        if row:
            site = dict(row)
            site["fotos"] = json.loads(site.get("fotos") or "[]")
            site["redes_sociais"] = json.loads(site.get("redes_sociais") or "{}")
            return site
        return None
    finally:
        conn.close()


def buscar_site_por_slug(slug: str) -> Optional[dict]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sites WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        if row:
            site = dict(row)
            site["fotos"] = json.loads(site.get("fotos") or "[]")
            site["redes_sociais"] = json.loads(site.get("redes_sociais") or "{}")
            return site
        return None
    finally:
        conn.close()


def listar_sites_usuario(user_id: int) -> list:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM sites WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        sites = []
        for row in cursor.fetchall():
            site = dict(row)
            site["fotos"] = json.loads(site.get("fotos") or "[]")
            site["redes_sociais"] = json.loads(site.get("redes_sociais") or "{}")
            sites.append(site)
        return sites
    finally:
        conn.close()


def atualizar_site(site_id: int, dados: dict) -> Optional[dict]:
    conn = get_connection()
    try:
        campos = []
        valores = []
        for campo in ["nome_negocio", "descricao", "segmento", "telefone",
                       "whatsapp", "email_contato", "endereco", "template_id",
                       "cor_primaria", "cor_secundaria", "cor_texto",
                       "logo_url", "slug", "status", "html_gerado", "site_url"]:
            if campo in dados:
                campos.append(f"{campo} = ?")
                valores.append(dados[campo])

        if "fotos" in dados:
            campos.append("fotos = ?")
            valores.append(json.dumps(dados["fotos"]))

        if "redes_sociais" in dados:
            campos.append("redes_sociais = ?")
            valores.append(json.dumps(dados["redes_sociais"]))

        if not campos:
            return buscar_site_por_id(site_id)

        campos.append("updated_at = ?")
        valores.append(datetime.now().isoformat())
        valores.append(site_id)

        conn.execute(
            f"UPDATE sites SET {', '.join(campos)} WHERE id = ?",
            valores
        )
        conn.commit()
        return buscar_site_por_id(site_id)
    finally:
        conn.close()


def deletar_site(site_id: int, user_id: int) -> bool:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sites WHERE id = ? AND user_id = ?", (site_id, user_id))
        conn.commit()
        if cursor.rowcount > 0:
            decrementar_sites_criados(user_id)
            return True
        return False
    finally:
        conn.close()


def contar_sites_usuario(user_id: int) -> int:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sites WHERE user_id = ?", (user_id,))
        return cursor.fetchone()[0]
    finally:
        conn.close()


# ========== SUBSCRIPTIONS ==========

def criar_assinatura(user_id: int, plano: str = "pro", valor: float = 69.90,
                     payment_gateway: str = None, external_id: str = None) -> dict:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO subscriptions (user_id, plano, valor, status, payment_gateway, external_subscription_id)
            VALUES (?, ?, ?, 'active', ?, ?)
        ''', (user_id, plano, valor, payment_gateway, external_id))
        conn.commit()
        atualizar_plano_usuario(user_id, plano)
        return buscar_assinatura_ativa(user_id)
    finally:
        conn.close()


def buscar_assinatura_ativa(user_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM subscriptions WHERE user_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def cancelar_assinatura(user_id: int) -> bool:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE subscriptions SET status = 'cancelled', fim = ? WHERE user_id = ? AND status = 'active'",
            (datetime.now().isoformat(), user_id)
        )
        conn.commit()
        atualizar_plano_usuario(user_id, "free")
        return True
    finally:
        conn.close()


# ========== PAYMENTS ==========

def registrar_pagamento(user_id: int, tipo: str, valor: float, descricao: str,
                        status: str = "pending", gateway: str = None,
                        external_id: str = None) -> dict:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (user_id, tipo, valor, descricao, status, payment_gateway, external_payment_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, tipo, valor, descricao, status, gateway, external_id))
        conn.commit()
        return {"id": cursor.lastrowid, "status": status}
    finally:
        conn.close()


def listar_pagamentos_usuario(user_id: int) -> list:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM payments WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


# ========== TEMPLATES ==========

def listar_templates() -> list:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM templates WHERE ativo = 1")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def buscar_template(template_id: str) -> Optional[dict]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ========== ADMIN STATS ==========

def estatisticas_plataforma() -> dict:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE plano = 'pro'")
        total_pro = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM sites")
        total_sites = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM sites WHERE status = 'publicado'")
        sites_publicados = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE status = 'active'")
        assinaturas_ativas = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(valor), 0) FROM payments WHERE status = 'completed'")
        receita_total = cursor.fetchone()[0]
        return {
            "total_usuarios": total_users,
            "usuarios_pro": total_pro,
            "total_sites": total_sites,
            "sites_publicados": sites_publicados,
            "assinaturas_ativas": assinaturas_ativas,
            "receita_total": receita_total
        }
    finally:
        conn.close()
