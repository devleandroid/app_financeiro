# logic/recomendador.py
import random
from typing import Dict, List

class Recomendador:
    """
    Classe responsável pela lógica de negócio de gerar recomendações.
    Agora usando dados de câmbio corretamente calculados.
    """
    
    def __init__(self):
        # Limiares para análise (ajuste conforme sua estratégia)
        self.limiares = {
            'dolar_forte': 5.0,      # Abaixo disso, real forte
            'dolar_fraco': 5.5,       # Acima disso, real fraco
            'euro_forte': 5.8,        # Abaixo disso, euro forte vs real
            'bitcoin_compra': 60000,   # Preço considerado bom para compra
        }
    
    def analisar_cenario_economico(self, dados_cambio: Dict[str, float]) -> Dict:
        """Analisa o cenário baseado nas taxas de câmbio"""
        cenarios = {
            'brasil': {},
            'eua': {},
            'europa': {},
            'china': {},
            'reino_unido': {}
        }
        
        # Análise do Real (BRL)
        if 'BRL' in dados_cambio:
            usd_brl = dados_cambio['BRL']  # USD → BRL
            cenarios['brasil']['dolar'] = usd_brl
            cenarios['brasil']['classificacao'] = (
                'forte' if usd_brl < self.limiares['dolar_forte']
                else 'fraco' if usd_brl > self.limiares['dolar_fraco']
                else 'neutro'
            )
        
        # Análise do Euro (EUR) vs Real
        if 'EUR' in dados_cambio and 'BRL' in dados_cambio:
            eur_brl = dados_cambio['EUR'] / dados_cambio['BRL']  # EUR → BRL
            cenarios['europa']['real'] = eur_brl
        
        # Análise da Libra (GBP)
        if 'GBP' in dados_cambio:
            cenarios['reino_unido']['usd'] = dados_cambio['GBP']
        
        # Análise do Yuan (CNY)
        if 'CNY' in dados_cambio:
            cenarios['china']['usd'] = dados_cambio['CNY']
        
        return cenarios
    
    def gerar_recomendacoes(self, dados: Dict) -> List[Dict]:
        """
        Gera 5 recomendações baseadas em análise real dos dados
        """
        dados_cambio = dados.get("cambio", {})
        dados_bitcoin = dados.get("bitcoin", {})
        
        # Analisar cenário
        cenarios = self.analisar_cenario_economico(dados_cambio)
        
        recomendacoes = []
        
        # 1. Recomendação baseada no Real
        if 'brasil' in cenarios:
            brl = cenarios['brasil']
            if brl.get('classificacao') == 'forte':
                recomendacoes.append({
                    "nome": "Ações de Exportação Brasileiras",
                    "prazo": "Curto Prazo",
                    "razao": f"Real forte (USD/BRL = {brl['dolar']:.2f}) favorece importação, mas empresas exportadoras podem sofrer. Foco em empresas com receita em dólar.",
                    "risco": "Médio",
                    "categoria": "Ações",
                    "pais": "Brasil"
                })
            elif brl.get('classificacao') == 'fraco':
                recomendacoes.append({
                    "nome": "Títulos Públicos Indexados ao Dólar",
                    "prazo": "Curto Prazo",
                    "razao": f"Real fraco (USD/BRL = {brl['dolar']:.2f}) pode continuar desvalorizando. Proteção cambial com títulos atrelados ao dólar.",
                    "risco": "Baixo",
                    "categoria": "Renda Fixa",
                    "pais": "Brasil"
                })
        
        # 2. Recomendação baseada em Dólar vs Euro
        if 'EUR' in dados_cambio and 'USD' in dados_cambio:
            eur_usd = 1 / dados_cambio['EUR']  # EUR → USD (invertendo)
            if eur_usd > 1.10:  # Euro forte
                recomendacoes.append({
                    "nome": "Bonds Europeus (Governo Alemão)",
                    "prazo": "Longo Prazo",
                    "razao": f"Euro forte (EUR/USD = {eur_usd:.2f}) e estabilidade econômica da zona do euro. Títulos alemães como porto seguro.",
                    "risco": "Baixo",
                    "categoria": "Renda Fixa",
                    "pais": "Alemanha"
                })
        
        # 3. Recomendação baseada em Bitcoin
        preco_btc = dados_bitcoin.get('preco', {}).get('price', 0)
        tendencia_btc = dados_bitcoin.get('tendencia', {}).get('trend', 'estável')
        
        if preco_btc < self.limiares['bitcoin_compra'] and tendencia_btc == 'alta':
            recomendacoes.append({
                "nome": "ETF de Bitcoin (QBTC11)",
                "prazo": "Longo Prazo",
                "razao": f"Bitcoin abaixo de US$ {self.limiares['bitcoin_compra']} com tendência de alta. Exposição regulada através de ETF.",
                "risco": "Alto",
                "categoria": "Cripto",
                "pais": "Global"
            })
        elif tendencia_btc == 'alta':
            recomendacoes.append({
                "nome": "Mineração de Bitcoin (Empresas)",
                "prazo": "Curto Prazo",
                "razao": "Tendência de alta do Bitcoin beneficia empresas de mineração, que têm alavancagem operacional ao preço da cripto.",
                "risco": "Alto",
                "categoria": "Ações",
                "pais": "Global"
            })
        
        # 4. Recomendação baseada em China
        if 'CNY' in dados_cambio:
            usd_cny = dados_cambio['CNY']
            if usd_cny > 7.0:  # Yuan desvalorizado
                recomendacoes.append({
                    "nome": "Ações de Consumo Chinês (Alibaba, Tencent)",
                    "prazo": "Longo Prazo",
                    "razao": f"Yuan desvalorizado (USD/CNY = {usd_cny:.2f}) pode impulsionar exportações chinesas. Empresas de tecnologia se beneficiam da retomada.",
                    "risco": "Médio-Alto",
                    "categoria": "Ações",
                    "pais": "China"
                })
        
        # 5. Recomendação baseada em diversificação global
        if len(dados_cambio) >= 3:
            recomendacoes.append({
                "nome": "ETF Global (ACWI - iShares MSCI World)",
                "prazo": "Longo Prazo",
                "razao": "Diversificação global com exposição a mercados desenvolvidos e emergentes. Proteção contra risco cambial específico.",
                "risco": "Médio",
                "categoria": "ETF",
                "pais": "Global"
            })
        
        # Garantir que temos 5 recomendações
        recomendacoes_padrao = [
            {
                "nome": "Tesouro IPCA+ (Títulos Públicos)",
                "prazo": "Longo Prazo",
                "razao": "Proteção contra inflação e juros reais atrativos no Brasil.",
                "risco": "Baixo",
                "categoria": "Renda Fixa",
                "pais": "Brasil"
            },
            {
                "nome": "Ações de Bancos Americanos (JPM, BAC)",
                "prazo": "Curto Prazo",
                "razao": "Cenário de juros altos nos EUA beneficia margem de bancos.",
                "risco": "Médio",
                "categoria": "Ações",
                "pais": "EUA"
            },
            {
                "nome": "Commodities (OURO, Soja, Petróleo)",
                "prazo": "Médio Prazo",
                "razao": "Hedge contra volatilidade cambial e tensões geopolíticas.",
                "risco": "Médio",
                "categoria": "Commodities",
                "pais": "Global"
            }
        ]
        
        # Preencher até ter 5 recomendações
        while len(recomendacoes) < 5:
            for rec in recomendacoes_padrao:
                if len(recomendacoes) < 5 and rec not in recomendacoes:
                    recomendacoes.append(rec)
        
        return recomendacoes[:5]