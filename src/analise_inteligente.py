# ============================================
# analise_inteligente.py - Módulo de IA para Análise de Dados
# ============================================
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import warnings
import os
warnings.filterwarnings('ignore')

class AnaliseInteligente:
    """Classe para análise inteligente de dados de vendas"""
    
    def __init__(self, conexao):
        self.conexao = conexao
        self.dados = {}
        self.insights = []
        self.metricas = {}
        
    def carregar_dados(self):
        """Carrega todos os dados necessários do banco"""
        print("📊 Carregando dados do banco...")
        
        # Query ajustada com os nomes corretos das colunas
        query_vendas = """
        SELECT 
            f.id_pedido,
            f.id_cliente,
            f.fk_id_produto,
            f.fk_id_data,
            f.Vendas as vendas,
            f.Quantidade as quantidade,
            f.Lucro as lucro,
            d.Data_Pedido as data_pedido,
            d.Ano as ano,
            d.Mes as mes,
            d.Mes_Nome as mes_nome,
            p.nome_produto,
            p.categoria,
            p.sub_categoria,
            c.nome_cliente,
            c.segmento,
            l.cidade,
            l.estado,
            l.regiao
        FROM fato_vendas f
        JOIN dim_data d ON f.fk_id_data = d.pk_id_data
        JOIN dim_produto p ON f.fk_id_produto = p.pk_id_produto
        JOIN dim_cliente c ON f.id_cliente = c.id_cliente
        JOIN dim_local l ON c.fk_id_local = l.pk_id_local
        """
        
        self.dados['vendas'] = pd.read_sql(query_vendas, self.conexao)
        
        # Converter data
        self.dados['vendas']['data_pedido'] = pd.to_datetime(self.dados['vendas']['data_pedido'])
        
        # Criar colunas adicionais úteis
        self.dados['vendas']['ano_mes'] = self.dados['vendas']['data_pedido'].dt.strftime('%Y-%m')
        self.dados['vendas']['trimestre'] = self.dados['vendas']['data_pedido'].dt.quarter
        self.dados['vendas']['dia_semana'] = self.dados['vendas']['data_pedido'].dt.day_name()
        
        print(f"✅ Dados carregados: {len(self.dados['vendas'])} registros")
        print(f"📅 Período: {self.dados['vendas']['data_pedido'].min().date()} a {self.dados['vendas']['data_pedido'].max().date()}")
        print(f"📊 Colunas disponíveis: {list(self.dados['vendas'].columns)}")
        
        return self.dados['vendas']
    
    def calcular_kpis(self):
        """Calcula KPIs principais do negócio"""
        print("\n" + "="*60)
        print("📈 CALCULANDO KPIS E MÉTRICAS")
        print("="*60)
        
        df = self.dados['vendas']
        
        # KPIs Gerais
        self.metricas['faturamento_total'] = df['vendas'].sum()
        self.metricas['lucro_total'] = df['lucro'].sum()
        self.metricas['margem_lucro'] = (self.metricas['lucro_total'] / self.metricas['faturamento_total']) * 100 if self.metricas['faturamento_total'] > 0 else 0
        self.metricas['ticket_medio'] = df['vendas'].mean()
        self.metricas['itens_por_pedido'] = df['quantidade'].mean()
        
        # KPIs de Clientes
        self.metricas['total_clientes'] = df['id_cliente'].nunique()
        self.metricas['freq_media_compras'] = df.groupby('id_cliente')['id_pedido'].count().mean()
        
        # KPIs de Produtos
        self.metricas['total_produtos'] = df['fk_id_produto'].nunique()
        
        # KPIs Temporais
        self.metricas['meses_analisados'] = df['ano_mes'].nunique()
        self.metricas['media_mensal'] = df.groupby('ano_mes')['vendas'].sum().mean()
        
        # Exibir KPIs
        print(f"\n💰 FATURAMENTO TOTAL: R$ {self.metricas['faturamento_total']:,.2f}")
        print(f"📈 LUCRO TOTAL: R$ {self.metricas['lucro_total']:,.2f}")
        print(f"📊 MARGEM DE LUCRO: {self.metricas['margem_lucro']:.2f}%")
        print(f"🎫 TICKET MÉDIO: R$ {self.metricas['ticket_medio']:.2f}")
        print(f"👥 TOTAL DE CLIENTES: {self.metricas['total_clientes']:,}")
        print(f"📦 TOTAL DE PRODUTOS: {self.metricas['total_produtos']:,}")
        print(f"📅 MESES ANALISADOS: {self.metricas['meses_analisados']}")
        print(f"📊 MÉDIA MENSAL: R$ {self.metricas['media_mensal']:,.2f}")
        
        return self.metricas
    
    def analise_temporal(self):
        """Análise de tendências temporais"""
        print("\n" + "="*60)
        print("📅 ANÁLISE TEMPORAL")
        print("="*60)
        
        df = self.dados['vendas']
        
        # Vendas por mês
        vendas_mensal = df.groupby(['ano', 'mes', 'mes_nome'])['vendas'].sum().reset_index()
        vendas_mensal = vendas_mensal.sort_values(['ano', 'mes'])
        
        if len(vendas_mensal) > 0:
            # Melhor e pior mês
            melhor_idx = vendas_mensal['vendas'].idxmax()
            pior_idx = vendas_mensal['vendas'].idxmin()
            melhor_mes = vendas_mensal.loc[melhor_idx]
            pior_mes = vendas_mensal.loc[pior_idx]
            
            print(f"\n🏆 MELHOR MÊS: {melhor_mes['mes_nome']}/{melhor_mes['ano']:.0f} - R$ {melhor_mes['vendas']:,.2f}")
            print(f"📉 PIOR MÊS: {pior_mes['mes_nome']}/{pior_mes['ano']:.0f} - R$ {pior_mes['vendas']:,.2f}")
        
        # Crescimento anual
        vendas_ano = df.groupby('ano')['vendas'].sum()
        if len(vendas_ano) > 1:
            crescimento_total = ((vendas_ano.iloc[-1] - vendas_ano.iloc[0]) / vendas_ano.iloc[0]) * 100
            print(f"\n📈 CRESCIMENTO TOTAL NO PERÍODO: {crescimento_total:.2f}%")
            
            # Crescimento ano a ano
            print(f"\n📊 CRESCIMENTO ANO A ANO:")
            for i in range(1, len(vendas_ano)):
                ano_atual = vendas_ano.index[i]
                ano_anterior = vendas_ano.index[i-1]
                crescimento_aa = ((vendas_ano.iloc[i] - vendas_ano.iloc[i-1]) / vendas_ano.iloc[i-1]) * 100
                print(f"   {ano_anterior:.0f} → {ano_atual:.0f}: {crescimento_aa:+.2f}%")
        
        # Sazonalidade - meses com mais vendas
        vendas_por_mes = df.groupby('mes')['vendas'].sum().sort_values(ascending=False)
        print(f"\n🗓️ MESES COM MAIORES VENDAS:")
        for mes, valor in vendas_por_mes.head(3).items():
            nome_mes = df[df['mes'] == mes]['mes_nome'].iloc[0]
            print(f"   {nome_mes}: R$ {valor:,.2f}")
        
        # Vendas por trimestre
        vendas_trimestre = df.groupby(['ano', 'trimestre'])['vendas'].sum().reset_index()
        print(f"\n📅 VENDAS POR TRIMESTRE:")
        for _, row in vendas_trimestre.iterrows():
            print(f"   {row['ano']:.0f}-T{row['trimestre']:.0f}: R$ {row['vendas']:,.2f}")
        
        self.metricas['vendas_mensal'] = vendas_mensal
        self.metricas['crescimento_anual'] = crescimento_total if len(vendas_ano) > 1 else 0
        
        return vendas_mensal

    def analise_produtos(self):
        """Análise detalhada de produtos"""
        print("\n" + "="*60)
        print("📦 ANÁLISE DE PRODUTOS")
        print("="*60)
        
        df = self.dados['vendas']
        
        # Top produtos por faturamento
        top_produtos = df.groupby(['categoria', 'sub_categoria', 'nome_produto']).agg({
            'vendas': 'sum',
            'quantidade': 'sum',
            'lucro': 'sum'
        }).sort_values('vendas', ascending=False).head(10)
        
        print("\n🏆 TOP 10 PRODUTOS POR FATURAMENTO:")
        for i, (idx, row) in enumerate(top_produtos.head(5).iterrows(), 1):
            nome_curto = idx[2][:50] if len(idx[2]) > 50 else idx[2]
            print(f"   {i}. {nome_curto}")
            print(f"      Faturamento: R$ {row['vendas']:,.2f} | Lucro: R$ {row['lucro']:,.2f}")
        
        # Análise por categoria
        categoria_performance = df.groupby('categoria').agg({
            'vendas': 'sum',
            'lucro': 'sum',
            'quantidade': 'sum'
        }).round(2)
        
        categoria_performance['margem'] = (categoria_performance['lucro'] / categoria_performance['vendas']) * 100
        categoria_performance['margem'] = categoria_performance['margem'].fillna(0)
        categoria_performance = categoria_performance.sort_values('vendas', ascending=False)
        
        print("\n📊 PERFORMANCE POR CATEGORIA:")
        for cat in categoria_performance.index:
            print(f"\n   {cat.upper()}:")
            print(f"      Faturamento: R$ {categoria_performance.loc[cat, 'vendas']:,.2f}")
            print(f"      Lucro: R$ {categoria_performance.loc[cat, 'lucro']:,.2f}")
            print(f"      Margem: {categoria_performance.loc[cat, 'margem']:.2f}%")
        
        # Produtos com margem negativa (prejuízo)
        produtos_prejuizo = df.groupby('nome_produto')['lucro'].sum()
        produtos_prejuizo = produtos_prejuizo[produtos_prejuizo < 0].sort_values()
        
        if len(produtos_prejuizo) > 0:
            prejuizo_total = abs(produtos_prejuizo.sum())
            print(f"\n⚠️ PRODUTOS COM PREJUÍZO: {len(produtos_prejuizo)} produtos")
            print(f"   Prejuízo total: R$ {prejuizo_total:,.2f}")
            print(f"   Piores produtos:")
            for i, (produto, valor) in enumerate(produtos_prejuizo.head(3).items(), 1):
                print(f"      {i}. {produto[:40]}: R$ {valor:,.2f}")
        
        self.metricas['top_produtos'] = top_produtos
        self.metricas['categoria_performance'] = categoria_performance
        self.metricas['produtos_prejuizo'] = len(produtos_prejuizo)
        
        return categoria_performance

    def analise_clientes(self):
        """Análise de clientes e segmentação"""
        print("\n" + "="*60)
        print("👥 ANÁLISE DE CLIENTES")
        print("="*60)
        
        df = self.dados['vendas']
        
        # Análise por segmento
        segmento_performance = df.groupby('segmento').agg({
            'vendas': 'sum',
            'lucro': 'sum',
            'id_cliente': 'nunique'
        }).round(2)
        
        segmento_performance['ticket_medio'] = segmento_performance['vendas'] / segmento_performance['id_cliente']
        segmento_performance['margem'] = (segmento_performance['lucro'] / segmento_performance['vendas']) * 100
        segmento_performance['margem'] = segmento_performance['margem'].fillna(0)
        
        print("\n📊 PERFORMANCE POR SEGMENTO:")
        for seg in segmento_performance.index:
            print(f"\n   {seg.upper()}:")
            print(f"      Clientes: {segmento_performance.loc[seg, 'id_cliente']:.0f}")
            print(f"      Faturamento: R$ {segmento_performance.loc[seg, 'vendas']:,.2f}")
            print(f"      Ticket Médio: R$ {segmento_performance.loc[seg, 'ticket_medio']:.2f}")
            print(f"      Margem: {segmento_performance.loc[seg, 'margem']:.2f}%")
        
        # Top clientes
        top_clientes = df.groupby(['id_cliente', 'nome_cliente', 'segmento']).agg({
            'vendas': 'sum',
            'lucro': 'sum',
            'id_pedido': 'count'
        }).rename(columns={'id_pedido': 'qtd_compras'}).sort_values('vendas', ascending=False).head(10)
        
        print("\n🏆 TOP 10 CLIENTES POR FATURAMENTO:")
        for i, (idx, row) in enumerate(top_clientes.head(5).iterrows(), 1):
            print(f"   {i}. {idx[1]} ({idx[2]})")
            print(f"      Total: R$ {row['vendas']:,.2f} | Compras: {row['qtd_compras']:.0f}")
        
        # Análise RFV
        data_atual = df['data_pedido'].max()
        
        rfv = df.groupby('id_cliente').agg({
            'data_pedido': lambda x: (data_atual - x.max()).days,
            'id_pedido': 'count',
            'vendas': 'sum'
        }).rename(columns={
            'data_pedido': 'recencia',
            'id_pedido': 'frequencia',
            'vendas': 'valor'
        })
        
        # Classificar clientes
        if len(rfv) >= 4:
            try:
                rfv['score_recencia'] = pd.qcut(rfv['recencia'], 4, labels=['Muito Recente', 'Recente', 'Antigo', 'Muito Antigo'], duplicates='drop')
                rfv['score_frequencia'] = pd.qcut(rfv['frequencia'], 4, labels=['Baixa', 'Média', 'Alta', 'Muito Alta'], duplicates='drop')
                rfv['score_valor'] = pd.qcut(rfv['valor'], 4, labels=['Baixo', 'Médio', 'Alto', 'Muito Alto'], duplicates='drop')
                
                # Clientes VIP
                clientes_vip = rfv[(rfv['score_frequencia'] == 'Muito Alta') & (rfv['score_valor'] == 'Muito Alto')]
                print(f"\n⭐ CLIENTES VIP (Alta frequência + Alto valor): {len(clientes_vip)} clientes")
                
                # Clientes em risco
                clientes_risco = rfv[(rfv['score_recencia'] == 'Muito Antigo') & (rfv['score_frequencia'] == 'Baixa')]
                print(f"⚠️ CLIENTES EM RISCO (Inativos + Baixa frequência): {len(clientes_risco)} clientes")
                
                # Ticket médio por segmento RFV
                print(f"\n📊 TICKET MÉDIO POR PERFIL:")
                for score in ['Muito Alto', 'Alto', 'Médio', 'Baixo']:
                    if score in rfv['score_valor'].values:
                        ticket = rfv[rfv['score_valor'] == score]['valor'].mean()
                        print(f"   {score}: R$ {ticket:,.2f}")
                
                self.metricas['clientes_vip'] = len(clientes_vip)
                self.metricas['clientes_risco'] = len(clientes_risco)
            except Exception as e:
                print(f"   (Classificação RFV: {str(e)[:50]})")
        
        self.metricas['segmento_performance'] = segmento_performance
        self.metricas['top_clientes'] = top_clientes
        
        return segmento_performance

    def analise_geografica(self):
        """Análise por região e localização"""
        print("\n" + "="*60)
        print("🌎 ANÁLISE GEOGRÁFICA")
        print("="*60)
        
        df = self.dados['vendas']
        
        # Performance por região
        regiao_performance = df.groupby('regiao').agg({
            'vendas': 'sum',
            'lucro': 'sum',
            'quantidade': 'sum',
            'id_cliente': 'nunique'
        }).round(2)
        
        regiao_performance['margem'] = (regiao_performance['lucro'] / regiao_performance['vendas']) * 100
        regiao_performance['margem'] = regiao_performance['margem'].fillna(0)
        regiao_performance['ticket_medio'] = regiao_performance['vendas'] / regiao_performance['id_cliente']
        regiao_performance = regiao_performance.sort_values('vendas', ascending=False)
        
        print("\n📊 PERFORMANCE POR REGIÃO:")
        for reg in regiao_performance.index:
            print(f"\n   {reg}:")
            print(f"      Faturamento: R$ {regiao_performance.loc[reg, 'vendas']:,.2f}")
            print(f"      Clientes: {regiao_performance.loc[reg, 'id_cliente']:.0f}")
            print(f"      Margem: {regiao_performance.loc[reg, 'margem']:.2f}%")
            print(f"      Ticket Médio: R$ {regiao_performance.loc[reg, 'ticket_medio']:.2f}")
        
        # Top cidades
        top_cidades = df.groupby(['estado', 'cidade']).agg({
            'vendas': 'sum',
            'lucro': 'sum'
        }).sort_values('vendas', ascending=False).head(10)
        
        print("\n🏙️ TOP 10 CIDADES POR FATURAMENTO:")
        for i, (idx, row) in enumerate(top_cidades.head(5).iterrows(), 1):
            print(f"   {i}. {idx[1]}/{idx[0]}")
            print(f"      Faturamento: R$ {row['vendas']:,.2f} | Lucro: R$ {row['lucro']:,.2f}")
        
        # Ranking de margem por região
        print(f"\n📊 RANKING DE MARGEM POR REGIÃO:")
        ranking_margem = regiao_performance.sort_values('margem', ascending=False)
        for i, (reg, row) in enumerate(ranking_margem.iterrows(), 1):
            print(f"   {i}. {reg}: {row['margem']:.2f}%")
        
        self.metricas['regiao_performance'] = regiao_performance
        self.metricas['top_cidades'] = top_cidades
        
        return regiao_performance

    def gerar_insights(self):
        """Gera insights automáticos baseados nos dados"""
        print("\n" + "="*60)
        print("💡 INSIGHTS E RECOMENDAÇÕES")
        print("="*60)
        
        df = self.dados['vendas']
        insights = []
        
        # Insight 1: Categoria mais rentável
        rentabilidade = df.groupby('categoria').agg({
            'lucro': 'sum',
            'vendas': 'sum'
        })
        rentabilidade['retorno'] = (rentabilidade['lucro'] / rentabilidade['vendas']) * 100
        rentabilidade['retorno'] = rentabilidade['retorno'].fillna(0)
        melhor_categoria = rentabilidade['retorno'].idxmax()
        pior_categoria = rentabilidade['retorno'].idxmin()
        
        insights.append({
            'titulo': 'Categorias Mais e Menos Rentáveis',
            'insight': f'Categoria {melhor_categoria} tem melhor margem ({rentabilidade.loc[melhor_categoria, "retorno"]:.1f}%). Categoria {pior_categoria} tem menor margem ({rentabilidade.loc[pior_categoria, "retorno"]:.1f}%).',
            'recomendacao': f'Focar investimentos em {melhor_categoria} e revisar estratégia para {pior_categoria}.'
        })
        
        # Insight 2: Sazonalidade
        vendas_mes = df.groupby('mes')['vendas'].sum()
        if len(vendas_mes) > 0:
            mes_pico = vendas_mes.idxmax()
            mes_baixa = vendas_mes.idxmin()
            nome_mes_pico = df[df['mes'] == mes_pico]['mes_nome'].iloc[0]
            nome_mes_baixa = df[df['mes'] == mes_baixa]['mes_nome'].iloc[0]
            diferenca = (vendas_mes.max() / vendas_mes.min()) if vendas_mes.min() > 0 else 0
            
            insights.append({
                'titulo': 'Sazonalidade de Vendas',
                'insight': f'{nome_mes_pico} é o mês de pico ({vendas_mes.max():,.0f}) e {nome_mes_baixa} o de menor movimento ({vendas_mes.min():,.0f}). Diferença de {diferenca:.1f}x.',
                'recomendacao': f'Planejar estoque e campanhas promocionais para {nome_mes_pico}. Criar estratégias para aquecer {nome_mes_baixa}.'
            })
        
        # Insight 3: Segmento de clientes
        segmento_analise = df.groupby('segmento').agg({
            'vendas': 'sum',
            'lucro': 'sum',
            'id_cliente': 'nunique'
        })
        segmento_analise['ticket_medio'] = segmento_analise['vendas'] / segmento_analise['id_cliente']
        melhor_segmento = segmento_analise['ticket_medio'].idxmax()
        maior_segmento = segmento_analise['vendas'].idxmax()
        
        insights.append({
            'titulo': 'Perfil de Clientes',
            'insight': f'Segmento {melhor_segmento} tem maior ticket médio (R$ {segmento_analise.loc[melhor_segmento, "ticket_medio"]:.0f}). {maior_segmento} é o que mais fatura (R$ {segmento_analise.loc[maior_segmento, "vendas"]:,.0f}).',
            'recomendacao': f'Desenvolver programas específicos para {melhor_segmento} e estratégias de retenção para {maior_segmento}.'
        })
        
        # Insight 4: Concentração de vendas
        top_10_produtos = df.groupby('nome_produto')['vendas'].sum().sort_values(ascending=False).head(10).sum()
        top_20_produtos = df.groupby('nome_produto')['vendas'].sum().sort_values(ascending=False).head(20).sum()
        concentracao_top10 = (top_10_produtos / df['vendas'].sum()) * 100
        concentracao_top20 = (top_20_produtos / df['vendas'].sum()) * 100
        
        insights.append({
            'titulo': 'Concentração de Vendas',
            'insight': f'Top 10 produtos representam {concentracao_top10:.1f}% do faturamento. Top 20 representam {concentracao_top20:.1f}%.',
            'recomendacao': 'Diversificar portfólio para reduzir dependência. Analisar potencial dos produtos restantes.'
        })
        
        # Insight 5: Performance regional
        regiao_analise = df.groupby('regiao').agg({
            'vendas': 'sum',
            'lucro': 'sum'
        })
        regiao_analise['margem'] = (regiao_analise['lucro'] / regiao_analise['vendas']) * 100
        melhor_regiao = regiao_analise['vendas'].idxmax()
        pior_margem_regiao = regiao_analise['margem'].idxmin()
        
        insights.append({
            'titulo': 'Performance Regional',
            'insight': f'Região {melhor_regiao} lidera em faturamento (R$ {regiao_analise.loc[melhor_regiao, "vendas"]:,.0f}). Região {pior_margem_regiao} tem menor margem ({regiao_analise.loc[pior_margem_regiao, "margem"]:.1f}%).',
            'recomendacao': f'Expandir operações bem-sucedidas da {melhor_regiao} para outras regiões. Investigar causa da baixa margem em {pior_margem_regiao}.'
        })
        
        # Insight 6: Produtos problemáticos
        produtos_negativos = df[df['lucro'] < 0]['nome_produto'].nunique()
        if produtos_negativos > 0:
            prejuizo_total = df[df['lucro'] < 0]['lucro'].sum()
            insights.append({
                'titulo': 'Produtos com Prejuízo',
                'insight': f'{produtos_negativos} produtos geraram prejuízo total de R$ {abs(prejuizo_total):,.0f}.',
                'recomendacao': 'Revisar precificação, descontos e custos destes produtos. Considerar descontinuação dos piores.'
            })
        
        # Insight 7: Crescimento
        if 'crescimento_anual' in self.metricas:
            crescimento = self.metricas['crescimento_anual']
            if crescimento > 0:
                insights.append({
                    'titulo': 'Tendência de Crescimento',
                    'insight': f'O negócio cresceu {crescimento:.1f}% no período analisado.',
                    'recomendacao': 'Manter estratégias que estão funcionando. Investir em ações que geraram este crescimento.'
                })
            else:
                insights.append({
                    'titulo': 'Tendência de Queda',
                    'insight': f'O negócio teve queda de {abs(crescimento):.1f}% no período.',
                    'recomendacao': 'Revisar estratégias de marketing, precificação e análise de concorrência.'
                })
        
        # Exibir insights formatados
        for i, insight in enumerate(insights, 1):
            print(f"\n{'='*50}")
            print(f"INSIGHT {i}: {insight['titulo']}")
            print(f"{'='*50}")
            print(f"💡 {insight['insight']}")
            print(f"\n🎯 RECOMENDAÇÃO: {insight['recomendacao']}")
        
        self.insights = insights
        return insights

    def gerar_relatorio_completo(self):
        """Gera relatório completo em HTML"""
        print("\n" + "="*60)
        print("📄 GERANDO RELATÓRIO COMPLETO")
        print("="*60)
        
        # Criar pasta de relatórios se não existir
        if not os.path.exists('relatorios_ia'):
            os.makedirs('relatorios_ia')
        
        # Gerar HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Relatório Inteligente - Análise de Vendas</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 15px; }}
                h3 {{ color: #555; margin-top: 20px; }}
                .kpi-grid {{ display: flex; flex-wrap: wrap; gap: 15px; margin: 20px 0; }}
                .kpi {{ flex: 1; min-width: 180px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; text-align: center; }}
                .kpi-value {{ font-size: 28px; font-weight: bold; }}
                .kpi-label {{ font-size: 14px; margin-top: 8px; opacity: 0.9; }}
                .insight {{ background: #e8f4f8; padding: 20px; margin: 15px 0; border-left: 4px solid #3498db; border-radius: 8px; }}
                .recomendacao {{ background: #fef9e7; padding: 20px; margin: 15px 0; border-left: 4px solid #f39c12; border-radius: 8px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #3498db; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
                .badge-positive {{ background: #2ecc71; color: white; }}
                .badge-negative {{ background: #e74c3c; color: white; }}
                .footer {{ text-align: center; margin-top: 50px; padding: 20px; color: #7f8c8d; font-size: 12px; border-top: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Relatório Inteligente de Vendas</h1>
                <p><strong>Data de geração:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                <p><strong>Período analisado:</strong> {self.dados['vendas']['data_pedido'].min().date()} a {self.dados['vendas']['data_pedido'].max().date()}</p>
                
                <h2>🎯 KPIs Principais</h2>
                <div class="kpi-grid">
                    <div class="kpi"><div class="kpi-value">R$ {self.metricas['faturamento_total']:,.0f}</div><div class="kpi-label">Faturamento Total</div></div>
                    <div class="kpi"><div class="kpi-value">R$ {self.metricas['lucro_total']:,.0f}</div><div class="kpi-label">Lucro Total</div></div>
                    <div class="kpi"><div class="kpi-value">{self.metricas['margem_lucro']:.1f}%</div><div class="kpi-label">Margem de Lucro</div></div>
                    <div class="kpi"><div class="kpi-value">R$ {self.metricas['ticket_medio']:.0f}</div><div class="kpi-label">Ticket Médio</div></div>
                    <div class="kpi"><div class="kpi-value">{self.metricas['total_clientes']:,}</div><div class="kpi-label">Total Clientes</div></div>
                    <div class="kpi"><div class="kpi-value">{self.metricas['total_produtos']:,}</div><div class="kpi-label">Total Produtos</div></div>
                </div>
                
                <h2>💡 Insights e Recomendações</h2>
        """
        
        for i, insight in enumerate(self.insights, 1):
            html += f"""
                <div class="insight">
                    <strong>📌 Insight {i}: {insight['titulo']}</strong><br>
                    💡 {insight['insight']}
                </div>
                <div class="recomendacao">
                    🎯 <strong>Recomendação:</strong> {insight['recomendacao']}
                </div>
            """
        
        # Tabela de categorias
        html += f"""
                <h2>📊 Performance por Categoria</h2>
                <table>
                    <tr><th>Categoria</th><th>Faturamento</th><th>Lucro</th><th>Margem</th></tr>
        """
        for cat, row in self.metricas['categoria_performance'].iterrows():
            margem_class = "badge-positive" if row['margem'] > 20 else "badge-negative"
            html += f"""
                <tr>
                    <td><strong>{cat}</strong></td>
                    <td>R$ {row['vendas']:,.2f}</td>
                    <td>R$ {row['lucro']:,.2f}</td>
                    <td><span class="badge {margem_class}">{row['margem']:.1f}%</span></td>
                </tr>
            """
        
        html += """
                </table>
                
                <h2>🏆 Top 10 Produtos por Faturamento</h2>
                <table>
                    <tr><th>#</th><th>Produto</th><th>Categoria</th><th>Faturamento</th><th>Lucro</th></tr>
        """
        
        for i, (idx, row) in enumerate(self.metricas['top_produtos'].head(10).iterrows(), 1):
            nome_curto = idx[2][:60] if len(idx[2]) > 60 else idx[2]
            lucro_class = "badge-positive" if row['lucro'] > 0 else "badge-negative"
            html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{nome_curto}</td>
                    <td>{idx[0]}</td>
                    <td>R$ {row['vendas']:,.2f}</td>
                    <td><span class="badge {lucro_class}">R$ {row['lucro']:,.2f}</span></td>
                </tr>
            """
        
        html += f"""
                </table>
                
                <h2>🌎 Performance por Região</h2>
                <table>
                    <tr><th>Região</th><th>Faturamento</th><th>Clientes</th><th>Ticket Médio</th><th>Margem</th></tr>
        """
        
        for reg, row in self.metricas['regiao_performance'].iterrows():
            html += f"""
                <tr>
                    <td><strong>{reg}</strong></td>
                    <td>R$ {row['vendas']:,.2f}</td>
                    <td>{row['id_cliente']:.0f}</td>
                    <td>R$ {row['ticket_medio']:.2f}</td>
                    <td>{row['margem']:.1f}%</td>
                </tr>
            """
        
        html += f"""
                </table>
                
                <div class="footer">
                    📊 Relatório gerado automaticamente por IA - Sistema de Análise Inteligente de Dados<br>
                    🔄 Próxima atualização: {datetime.now().strftime('%d/%m/%Y')}
                </div>
            </div>
        </body>
        </html>
        """
        
        # Salvar HTML
        filename = f"relatorios_ia/relatorio_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Relatório gerado: {filename}")
        
        # Também gerar CSV com resumo
        resumo = {
            'data_analise': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'faturamento_total': self.metricas['faturamento_total'],
            'lucro_total': self.metricas['lucro_total'],
            'margem_lucro': self.metricas['margem_lucro'],
            'ticket_medio': self.metricas['ticket_medio'],
            'total_clientes': self.metricas['total_clientes'],
            'total_produtos': self.metricas['total_produtos'],
            'meses_analisados': self.metricas['meses_analisados']
        }
        
        df_resumo = pd.DataFrame([resumo])
        df_resumo.to_csv('relatorios_ia/resumo_executivo.csv', index=False, encoding='utf-8-sig')
        print(f"✅ Resumo executivo: relatorios_ia/resumo_executivo.csv")
        
        return filename

    def executar_analise_completa(self):
        """Executa todas as análises"""
        print("\n" + "🚀"*30)
        print("INICIANDO ANALISE INTELIGENTE DE DADOS")
        print("🚀"*30)
        
        self.carregar_dados()
        self.calcular_kpis()
        self.analise_temporal()
        self.analise_produtos()
        self.analise_clientes()
        self.analise_geografica()
        self.gerar_insights()
        
        # Salvar métricas em CSV
        if not os.path.exists('relatorios_ia'):
            os.makedirs('relatorios_ia')
        
        # Gerar relatório HTML
        relatorio_file = self.gerar_relatorio_completo()
        
        print("\n" + "="*60)
        print("✅ ANALISE CONCLUIDA COM SUCESSO!")
        print("="*60)
        print(f"📄 Relatório HTML: {relatorio_file}")
        print(f"📊 Resumo CSV: relatorios_ia/resumo_executivo.csv")
        print(f"💡 Total de insights gerados: {len(self.insights)}")
        print("="*60)
        
        return self.insights, self.metricas

# ============================================
# FUNÇÃO PRINCIPAL
# ============================================
def main():
    """Executa a análise inteligente"""
    from urllib.parse import quote_plus
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     SISTEMA DE ANÁLISE INTELIGENTE DE DADOS - VENDAS     ║
    ║                  IA para Tomada de Decisão               ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Configuração do banco
    config = {
        'usuario': 'root',
        'senha': 'Limites1007@',
        'host': '127.0.0.1',
        'porta': 3306,
        'banco': 'empresa_analitica'
    }
    
    try:
        # Criar conexão
        url_senha = quote_plus(config['senha'])
        conexao = create_engine(
            f"mysql+pymysql://{config['usuario']}:{url_senha}@{config['host']}:{config['porta']}/{config['banco']}",
            pool_pre_ping=True
        )
        
        # Executar análise
        analise = AnaliseInteligente(conexao)
        insights, metricas = analise.executar_analise_completa()
        
        print("\n✨ Análise finalizada! Abra o arquivo HTML para visualizar o relatório completo.")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()