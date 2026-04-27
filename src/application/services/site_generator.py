"""
Servico de geracao de sites HTML a partir de templates.

Gera landing pages completas usando templates Jinja2-like
com substituicao de variaveis do usuario.
"""
import os
import re
import json
import logging
from pathlib import Path
from typing import Optional

from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


TEMPLATE_RESTAURANTE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{nome_negocio}}</title>
    <meta name="description" content="{{descricao}}">
    <meta property="og:title" content="{{nome_negocio}}">
    <meta property="og:description" content="{{descricao}}">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: {{cor_texto}}; }
        .hero { background: linear-gradient(135deg, {{cor_primaria}}, {{cor_secundaria}}); min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; padding: 2rem; }
        .hero h1 { font-size: 3.5rem; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .hero p { font-size: 1.3rem; max-width: 600px; margin: 0 auto 2rem; opacity: 0.9; }
        .btn { display: inline-block; padding: 15px 40px; background: #fff; color: {{cor_primaria}}; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 1.1rem; transition: transform 0.3s, box-shadow 0.3s; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .section { padding: 80px 20px; max-width: 1200px; margin: 0 auto; }
        .section-dark { background: {{cor_secundaria}}; color: {{cor_texto}}; padding: 80px 20px; }
        .section-light { background: #f8f9fa; color: #333; padding: 80px 20px; }
        .section h2 { font-size: 2.5rem; text-align: center; margin-bottom: 3rem; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; max-width: 1200px; margin: 0 auto; }
        .feature-card { background: rgba(255,255,255,0.1); border-radius: 16px; padding: 2rem; text-align: center; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
        .feature-card .icon { font-size: 3rem; margin-bottom: 1rem; }
        .feature-card h3 { font-size: 1.3rem; margin-bottom: 0.5rem; }
        .contact { background: {{cor_primaria}}; color: white; padding: 80px 20px; text-align: center; }
        .contact h2 { margin-bottom: 2rem; }
        .contact-info { display: flex; flex-wrap: wrap; justify-content: center; gap: 2rem; margin-top: 2rem; }
        .contact-item { background: rgba(255,255,255,0.15); padding: 1.5rem 2rem; border-radius: 12px; min-width: 250px; }
        .contact-item .label { font-size: 0.9rem; opacity: 0.8; margin-bottom: 0.3rem; }
        .contact-item .value { font-size: 1.2rem; font-weight: bold; }
        .contact-item a { color: white; text-decoration: none; }
        .footer { background: #111; color: #888; text-align: center; padding: 2rem; font-size: 0.9rem; }
        .whatsapp-float { position: fixed; bottom: 20px; right: 20px; background: #25D366; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; text-decoration: none; box-shadow: 0 4px 15px rgba(0,0,0,0.3); z-index: 1000; transition: transform 0.3s; }
        .whatsapp-float:hover { transform: scale(1.1); }
        @media (max-width: 768px) { .hero h1 { font-size: 2.2rem; } .hero p { font-size: 1rem; } .section h2 { font-size: 1.8rem; } }
    </style>
</head>
<body>
    <section class="hero">
        <div>
            <h1>{{nome_negocio}}</h1>
            <p>{{descricao}}</p>
            <a href="#contato" class="btn">Fale Conosco</a>
        </div>
    </section>

    <section class="section-dark">
        <h2>Por que nos escolher?</h2>
        <div class="features">
            <div class="feature-card">
                <div class="icon">&#127860;</div>
                <h3>Qualidade Premium</h3>
                <p>Ingredientes selecionados e preparo artesanal para uma experiencia unica</p>
            </div>
            <div class="feature-card">
                <div class="icon">&#128337;</div>
                <h3>Atendimento Rapido</h3>
                <p>Servico agil sem perder a qualidade que voce merece</p>
            </div>
            <div class="feature-card">
                <div class="icon">&#127775;</div>
                <h3>Ambiente Acolhedor</h3>
                <p>Espaco pensado para voce se sentir em casa</p>
            </div>
        </div>
    </section>

    <section class="section-light">
        <div class="section">
            <h2>Sobre Nos</h2>
            <p style="text-align:center; max-width:700px; margin:0 auto; font-size:1.1rem; line-height:1.8;">
                {{descricao}} Estamos localizados em <strong>{{endereco}}</strong>.
                Venha nos visitar e conheca nosso espaco!
            </p>
        </div>
    </section>

    <section class="contact" id="contato">
        <h2>Entre em Contato</h2>
        <p>Estamos prontos para atender voce!</p>
        <div class="contact-info">
            {{contact_phone_block}}
            {{contact_whatsapp_block}}
            {{contact_email_block}}
            {{contact_address_block}}
        </div>
    </section>

    <footer class="footer">
        <p>&copy; 2025 {{nome_negocio}}. Todos os direitos reservados.</p>
        <p style="margin-top:0.5rem; font-size:0.8rem;">Criado com a plataforma SitesPro</p>
    </footer>

    {{whatsapp_float}}
</body>
</html>"""


TEMPLATE_LOJA = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{nome_negocio}}</title>
    <meta name="description" content="{{descricao}}">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .nav { background: {{cor_secundaria}}; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; position: fixed; width: 100%; top: 0; z-index: 100; }
        .nav h2 { color: {{cor_texto}}; }
        .nav a { color: {{cor_texto}}; text-decoration: none; margin-left: 1.5rem; opacity: 0.8; transition: opacity 0.3s; }
        .nav a:hover { opacity: 1; }
        .hero { background: linear-gradient(135deg, {{cor_primaria}}, {{cor_secundaria}}); min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; padding: 2rem; color: {{cor_texto}}; }
        .hero h1 { font-size: 3.5rem; margin-bottom: 1rem; }
        .hero p { font-size: 1.3rem; max-width: 600px; margin: 0 auto 2rem; opacity: 0.9; }
        .btn { display: inline-block; padding: 15px 40px; background: #fff; color: {{cor_primaria}}; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 1.1rem; transition: all 0.3s; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .section { padding: 80px 20px; max-width: 1200px; margin: 0 auto; }
        .section h2 { font-size: 2.5rem; text-align: center; margin-bottom: 3rem; color: {{cor_secundaria}}; }
        .products { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
        .product-card { border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); transition: transform 0.3s; background: white; }
        .product-card:hover { transform: translateY(-5px); }
        .product-card .img-placeholder { height: 200px; background: linear-gradient(135deg, {{cor_primaria}}40, {{cor_secundaria}}40); display: flex; align-items: center; justify-content: center; font-size: 3rem; }
        .product-card .info { padding: 1.5rem; }
        .product-card h3 { margin-bottom: 0.5rem; color: {{cor_secundaria}}; }
        .product-card p { color: #666; font-size: 0.95rem; }
        .cta { background: {{cor_primaria}}; color: white; text-align: center; padding: 80px 20px; }
        .cta h2 { margin-bottom: 1rem; }
        .cta p { margin-bottom: 2rem; opacity: 0.9; font-size: 1.1rem; }
        .contact { background: {{cor_secundaria}}; color: {{cor_texto}}; padding: 60px 20px; text-align: center; }
        .contact-grid { display: flex; flex-wrap: wrap; justify-content: center; gap: 2rem; margin-top: 2rem; }
        .contact-item { background: rgba(255,255,255,0.1); padding: 1.5rem 2rem; border-radius: 12px; min-width: 220px; }
        .contact-item a { color: {{cor_texto}}; text-decoration: none; }
        .footer { background: #111; color: #666; text-align: center; padding: 2rem; }
        .whatsapp-float { position: fixed; bottom: 20px; right: 20px; background: #25D366; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; text-decoration: none; box-shadow: 0 4px 15px rgba(0,0,0,0.3); z-index: 1000; transition: transform 0.3s; }
        .whatsapp-float:hover { transform: scale(1.1); }
        @media (max-width: 768px) { .hero h1 { font-size: 2.2rem; } .nav { flex-direction: column; gap: 0.5rem; } }
    </style>
</head>
<body>
    <nav class="nav">
        <h2>{{nome_negocio}}</h2>
        <div>
            <a href="#produtos">Produtos</a>
            <a href="#contato">Contato</a>
        </div>
    </nav>

    <section class="hero">
        <div>
            <h1>{{nome_negocio}}</h1>
            <p>{{descricao}}</p>
            <a href="#contato" class="btn">Conheca Nossos Produtos</a>
        </div>
    </section>

    <section class="section" id="produtos">
        <h2>Nossos Destaques</h2>
        <div class="products">
            <div class="product-card">
                <div class="img-placeholder">&#128717;</div>
                <div class="info"><h3>Produto Destaque 1</h3><p>Qualidade e preco justo para voce</p></div>
            </div>
            <div class="product-card">
                <div class="img-placeholder">&#127873;</div>
                <div class="info"><h3>Produto Destaque 2</h3><p>As melhores ofertas da regiao</p></div>
            </div>
            <div class="product-card">
                <div class="img-placeholder">&#128142;</div>
                <div class="info"><h3>Produto Destaque 3</h3><p>Exclusividade e sofisticacao</p></div>
            </div>
        </div>
    </section>

    <section class="cta">
        <h2>Nao perca nossas ofertas!</h2>
        <p>Entre em contato e garanta as melhores condicoes</p>
        <a href="#contato" class="btn" style="color:{{cor_primaria}}">Fale Conosco</a>
    </section>

    <section class="contact" id="contato">
        <h2>Contato</h2>
        <div class="contact-grid">
            {{contact_phone_block}}
            {{contact_whatsapp_block}}
            {{contact_email_block}}
            {{contact_address_block}}
        </div>
    </section>

    <footer class="footer">
        <p>&copy; 2025 {{nome_negocio}}. Todos os direitos reservados.</p>
        <p style="margin-top:0.5rem; font-size:0.8rem;">Criado com a plataforma SitesPro</p>
    </footer>

    {{whatsapp_float}}
</body>
</html>"""


TEMPLATE_PORTFOLIO = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{nome_negocio}}</title>
    <meta name="description" content="{{descricao}}">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0a0a; color: #fff; }
        .hero { min-height: 100vh; display: flex; align-items: center; padding: 0 10%; background: linear-gradient(135deg, {{cor_secundaria}}, #0a0a0a); }
        .hero-content { max-width: 600px; }
        .hero h1 { font-size: 3.5rem; margin-bottom: 1rem; background: linear-gradient(135deg, {{cor_primaria}}, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero p { font-size: 1.2rem; line-height: 1.8; opacity: 0.8; margin-bottom: 2rem; }
        .btn { display: inline-block; padding: 14px 36px; background: {{cor_primaria}}; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; transition: all 0.3s; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px {{cor_primaria}}50; }
        .section { padding: 100px 10%; }
        .section h2 { font-size: 2.5rem; margin-bottom: 1rem; }
        .section .subtitle { opacity: 0.6; margin-bottom: 3rem; font-size: 1.1rem; }
        .services { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; }
        .service-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 2rem; transition: all 0.3s; }
        .service-card:hover { background: rgba(255,255,255,0.1); border-color: {{cor_primaria}}; }
        .service-card .num { font-size: 2rem; font-weight: bold; color: {{cor_primaria}}; margin-bottom: 1rem; }
        .service-card h3 { font-size: 1.3rem; margin-bottom: 0.5rem; }
        .service-card p { opacity: 0.7; line-height: 1.6; }
        .contact-section { background: {{cor_secundaria}}; border-radius: 24px; padding: 60px; margin: 0 10% 100px; text-align: center; }
        .contact-section h2 { margin-bottom: 1rem; }
        .contact-section p { opacity: 0.7; margin-bottom: 2rem; }
        .contact-links { display: flex; flex-wrap: wrap; justify-content: center; gap: 1.5rem; }
        .contact-link { background: rgba(255,255,255,0.1); padding: 1rem 2rem; border-radius: 12px; color: white; text-decoration: none; transition: background 0.3s; }
        .contact-link:hover { background: {{cor_primaria}}; }
        .footer { text-align: center; padding: 2rem; color: #555; font-size: 0.9rem; }
        .whatsapp-float { position: fixed; bottom: 20px; right: 20px; background: #25D366; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; text-decoration: none; box-shadow: 0 4px 15px rgba(0,0,0,0.3); z-index: 1000; transition: transform 0.3s; }
        .whatsapp-float:hover { transform: scale(1.1); }
        @media (max-width: 768px) { .hero { padding: 2rem; } .hero h1 { font-size: 2.2rem; } .section { padding: 60px 5%; } .contact-section { margin: 0 5% 60px; padding: 40px 20px; } }
    </style>
</head>
<body>
    <section class="hero">
        <div class="hero-content">
            <h1>{{nome_negocio}}</h1>
            <p>{{descricao}}</p>
            <a href="#contato" class="btn">Solicitar Orcamento</a>
        </div>
    </section>

    <section class="section">
        <h2>Nossos Servicos</h2>
        <p class="subtitle">Solucoes profissionais para o seu negocio</p>
        <div class="services">
            <div class="service-card">
                <div class="num">01</div>
                <h3>Consultoria</h3>
                <p>Analise completa e estrategias personalizadas para o seu projeto</p>
            </div>
            <div class="service-card">
                <div class="num">02</div>
                <h3>Desenvolvimento</h3>
                <p>Execucao profissional com qualidade e prazo garantidos</p>
            </div>
            <div class="service-card">
                <div class="num">03</div>
                <h3>Suporte Continuo</h3>
                <p>Acompanhamento e manutencao para resultados duradouros</p>
            </div>
        </div>
    </section>

    <div class="contact-section" id="contato">
        <h2>Vamos Conversar?</h2>
        <p>Entre em contato e transforme sua ideia em realidade</p>
        <div class="contact-links">
            {{contact_links}}
        </div>
    </div>

    <footer class="footer">
        <p>&copy; 2025 {{nome_negocio}}. Todos os direitos reservados.</p>
        <p style="margin-top:0.5rem;">Criado com a plataforma SitesPro</p>
    </footer>

    {{whatsapp_float}}
</body>
</html>"""


TEMPLATE_SAUDE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{nome_negocio}}</title>
    <meta name="description" content="{{descricao}}">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .hero { background: linear-gradient(135deg, {{cor_primaria}}, {{cor_secundaria}}); min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; padding: 2rem; color: {{cor_texto}}; }
        .hero h1 { font-size: 3.5rem; margin-bottom: 1rem; }
        .hero p { font-size: 1.3rem; max-width: 600px; margin: 0 auto 2rem; opacity: 0.9; }
        .btn { display: inline-block; padding: 15px 40px; background: white; color: {{cor_primaria}}; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 1.1rem; transition: all 0.3s; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .section { padding: 80px 20px; max-width: 1100px; margin: 0 auto; }
        .section h2 { font-size: 2.5rem; text-align: center; margin-bottom: 1rem; color: {{cor_secundaria}}; }
        .section .subtitle { text-align: center; color: #666; margin-bottom: 3rem; }
        .benefits { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; }
        .benefit { text-align: center; padding: 2rem; border-radius: 16px; background: #f8f9fa; }
        .benefit .icon { font-size: 3rem; margin-bottom: 1rem; }
        .benefit h3 { color: {{cor_primaria}}; margin-bottom: 0.5rem; }
        .benefit p { color: #666; line-height: 1.6; }
        .cta-section { background: linear-gradient(135deg, {{cor_primaria}}, {{cor_secundaria}}); color: white; text-align: center; padding: 80px 20px; }
        .cta-section h2 { margin-bottom: 1rem; font-size: 2.2rem; }
        .cta-section p { margin-bottom: 2rem; opacity: 0.9; }
        .contact-section { background: #f8f9fa; padding: 60px 20px; text-align: center; }
        .contact-section h2 { color: {{cor_secundaria}}; margin-bottom: 2rem; }
        .contact-cards { display: flex; flex-wrap: wrap; justify-content: center; gap: 1.5rem; }
        .contact-card { background: white; padding: 1.5rem 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); min-width: 230px; }
        .contact-card .label { font-size: 0.85rem; color: #999; margin-bottom: 0.3rem; }
        .contact-card .value { font-size: 1.1rem; font-weight: 600; color: {{cor_secundaria}}; }
        .contact-card a { color: {{cor_primaria}}; text-decoration: none; }
        .footer { background: {{cor_secundaria}}; color: rgba(255,255,255,0.6); text-align: center; padding: 2rem; font-size: 0.9rem; }
        .whatsapp-float { position: fixed; bottom: 20px; right: 20px; background: #25D366; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; text-decoration: none; box-shadow: 0 4px 15px rgba(0,0,0,0.3); z-index: 1000; transition: transform 0.3s; }
        .whatsapp-float:hover { transform: scale(1.1); }
        @media (max-width: 768px) { .hero h1 { font-size: 2.2rem; } }
    </style>
</head>
<body>
    <section class="hero">
        <div>
            <h1>{{nome_negocio}}</h1>
            <p>{{descricao}}</p>
            <a href="#contato" class="btn">Agendar Consulta</a>
        </div>
    </section>

    <section class="section">
        <h2>Nossos Diferenciais</h2>
        <p class="subtitle">Cuidando da sua saude com excelencia</p>
        <div class="benefits">
            <div class="benefit">
                <div class="icon">&#129657;</div>
                <h3>Profissionais Qualificados</h3>
                <p>Equipe especializada e em constante atualizacao</p>
            </div>
            <div class="benefit">
                <div class="icon">&#128153;</div>
                <h3>Atendimento Humanizado</h3>
                <p>Voce e tratado com carinho e atencao individual</p>
            </div>
            <div class="benefit">
                <div class="icon">&#127968;</div>
                <h3>Estrutura Moderna</h3>
                <p>Ambiente confortavel com equipamentos de ultima geracao</p>
            </div>
        </div>
    </section>

    <section class="cta-section">
        <h2>Sua saude em primeiro lugar!</h2>
        <p>Agende sua consulta e cuide de voce</p>
        <a href="#contato" class="btn" style="color:{{cor_primaria}}">Agendar Agora</a>
    </section>

    <section class="contact-section" id="contato">
        <h2>Contato</h2>
        <div class="contact-cards">
            {{contact_phone_block}}
            {{contact_whatsapp_block}}
            {{contact_email_block}}
            {{contact_address_block}}
        </div>
    </section>

    <footer class="footer">
        <p>&copy; 2025 {{nome_negocio}}. Todos os direitos reservados.</p>
        <p style="margin-top:0.5rem;">Criado com a plataforma SitesPro</p>
    </footer>

    {{whatsapp_float}}
</body>
</html>"""


TEMPLATES = {
    "restaurante": TEMPLATE_RESTAURANTE,
    "loja": TEMPLATE_LOJA,
    "portfolio": TEMPLATE_PORTFOLIO,
    "saude": TEMPLATE_SAUDE,
}


def _gerar_bloco_contato_phone(telefone: str) -> str:
    if not telefone:
        return ""
    return f'''<div class="contact-item contact-card">
        <div class="label">Telefone</div>
        <div class="value"><a href="tel:{telefone}">{telefone}</a></div>
    </div>'''


def _gerar_bloco_contato_whatsapp(whatsapp: str) -> str:
    if not whatsapp:
        return ""
    numero = re.sub(r'\D', '', whatsapp)
    return f'''<div class="contact-item contact-card">
        <div class="label">WhatsApp</div>
        <div class="value"><a href="https://wa.me/55{numero}" target="_blank">{whatsapp}</a></div>
    </div>'''


def _gerar_bloco_contato_email(email: str) -> str:
    if not email:
        return ""
    return f'''<div class="contact-item contact-card">
        <div class="label">Email</div>
        <div class="value"><a href="mailto:{email}">{email}</a></div>
    </div>'''


def _gerar_bloco_contato_endereco(endereco: str) -> str:
    if not endereco:
        return ""
    return f'''<div class="contact-item contact-card">
        <div class="label">Endereco</div>
        <div class="value">{endereco}</div>
    </div>'''


def _gerar_whatsapp_float(whatsapp: str) -> str:
    if not whatsapp:
        return ""
    numero = re.sub(r'\D', '', whatsapp)
    return f'<a href="https://wa.me/55{numero}" class="whatsapp-float" target="_blank">&#128172;</a>'


def _gerar_contact_links(dados: dict) -> str:
    links = []
    if dados.get("telefone"):
        links.append(f'<a href="tel:{dados["telefone"]}" class="contact-link">&#128222; {dados["telefone"]}</a>')
    if dados.get("whatsapp"):
        numero = re.sub(r'\D', '', dados["whatsapp"])
        links.append(f'<a href="https://wa.me/55{numero}" class="contact-link" target="_blank">&#128172; WhatsApp</a>')
    if dados.get("email_contato"):
        links.append(f'<a href="mailto:{dados["email_contato"]}" class="contact-link">&#9993; Email</a>')
    if dados.get("endereco"):
        links.append(f'<span class="contact-link">&#128205; {dados["endereco"]}</span>')
    return "\n            ".join(links)


def gerar_html_site(dados: dict) -> str:
    """
    Gera o HTML completo de um site a partir dos dados fornecidos.

    Args:
        dados: dicionario com nome_negocio, descricao, template_id, etc.

    Returns:
        String com o HTML completo do site gerado.
    """
    template_id = dados.get("template_id", "restaurante")
    template_html = TEMPLATES.get(template_id, TEMPLATE_RESTAURANTE)

    replacements = {
        "{{nome_negocio}}": dados.get("nome_negocio", "Meu Negocio"),
        "{{descricao}}": dados.get("descricao", ""),
        "{{endereco}}": dados.get("endereco", ""),
        "{{cor_primaria}}": dados.get("cor_primaria", "#2563eb"),
        "{{cor_secundaria}}": dados.get("cor_secundaria", "#1e1e2e"),
        "{{cor_texto}}": dados.get("cor_texto", "#ffffff"),
        "{{contact_phone_block}}": _gerar_bloco_contato_phone(dados.get("telefone", "")),
        "{{contact_whatsapp_block}}": _gerar_bloco_contato_whatsapp(dados.get("whatsapp", "")),
        "{{contact_email_block}}": _gerar_bloco_contato_email(dados.get("email_contato", "")),
        "{{contact_address_block}}": _gerar_bloco_contato_endereco(dados.get("endereco", "")),
        "{{whatsapp_float}}": _gerar_whatsapp_float(dados.get("whatsapp", "")),
        "{{contact_links}}": _gerar_contact_links(dados),
    }

    html = template_html
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    return html


def salvar_site_html(slug: str, html: str) -> str:
    """Salva o HTML gerado em um arquivo."""
    sites_dir = settings.GENERATED_SITES_DIR
    os.makedirs(sites_dir, exist_ok=True)

    file_path = os.path.join(sites_dir, f"{slug}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"Site salvo em: {file_path}")
    return file_path
