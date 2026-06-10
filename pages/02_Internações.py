import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# coloca a pasta raiz no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import carregar_tabela, criar_engine
from src.charts import injetar_custom_css, aplicar_estilo_layout, obter_paleta_cores

# configuracao da pagina
st.set_page_config(page_title="Internações SIH | DATASUS", layout="wide")
st.markdown(injetar_custom_css(), unsafe_allow_html=True)

# cores e conexao com o banco
colors = obter_paleta_cores()
_, db_type = criar_engine()

# titulo
st.title("Internações Hospitalares - SIH")
st.caption(f"Fonte: SIH (Sistema de Informacoes Hospitalares) / DATASUS | Banco de dados: {db_type.upper()}")
st.markdown("---")

try:
    df_int = carregar_tabela("internacoes")
except Exception as e:
    st.error("Erro ao conectar ao banco de dados ou carregar tabelas de internacoes. Verifique se realizou a ingestão de dados.")
    st.info("Execute: python src/ingest.py no terminal.")
    st.stop()

try:
    # Identifica colunas de anos
    anos = [c for c in df_int.columns if c.isdigit()]
    
    # KPIs principais
    total_acumulado = int(df_int[anos].sum().sum())
    
    # Encontra a principal causa histórica
    df_int["Total_Causa"] = df_int[anos].sum(axis=1)
    causa_lider_row = df_int.sort_values(by="Total_Causa", ascending=False).iloc[0]
    causa_lider_nome = causa_lider_row["capitulo_cid"]
    causa_lider_total = int(causa_lider_row["Total_Causa"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: {colors['internacoes']};">
                <div class="metric-title">Internações Acumuladas</div>
                <div class="metric-value">{total_acumulado:,}</div>
                <div class="metric-subtitle">Total geral registrado (2020-2026)</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: {colors['text_muted']};">
                <div class="metric-title">Causa Lider Historica</div>
                <div class="metric-value" style="font-size: 18px; line-height: 1.2; padding: 4px 0; font-family: 'Inter', sans-serif;">{causa_lider_nome}</div>
                <div class="metric-subtitle">Causa com maior volume de hospitalizacoes</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: {colors['success']};">
                <div class="metric-title">Volume da Causa Lider</div>
                <div class="metric-value">{causa_lider_total:,}</div>
                <div class="metric-subtitle">Internações ({causa_lider_total/total_acumulado*100:.1f}% do total geral)</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown("---")
    
    # Filtro integrado de busca
    st.markdown("### Pesquisa e Análise por Capitulo CID-10")
    
    # Barra deslizante de alternância rápida de anos (Controle de tempo)
    ano_selecionado = st.select_slider("Selecione o ano para análise no ranking", options=sorted(anos))
    
    # Caixa de busca em tempo real (Filtro por CID-10)
    busca_cid = st.text_input("Filtrar CID-10 por nome ou capitulo...", value="")
    
    # Filtra dados com base na busca
    df_filtrado_busca = df_int.copy()
    if busca_cid:
        df_filtrado_busca = df_filtrado_busca[
            df_filtrado_busca["capitulo_cid"].str.lower().str.contains(busca_cid.lower())
        ]
        
    tab_ranking, tab_tendencia = st.tabs(["Ranking por Ano", "Comparativo e Tendências"])
    
    with tab_ranking:
        if len(df_filtrado_busca) > 0:
            df_ranking = df_filtrado_busca[["capitulo_cid", ano_selecionado]].copy()
            df_ranking = df_ranking.sort_values(by=ano_selecionado, ascending=True)
            
            # Gráfico de Barras Horizontais em tons Indigo (Causa de hospitalizações)
            fig_rank = px.bar(
                df_ranking,
                x=ano_selecionado,
                y="capitulo_cid",
                orientation="h",
                title=f"Internações por Capitulo CID-10 - Ano {ano_selecionado}",
                color_discrete_sequence=[colors["internacoes"]],
                labels={"capitulo_cid": "Capitulo CID-10", ano_selecionado: "Internações"}
            )
            aplicar_estilo_layout(fig_rank, title=f"Internações por Capitulo CID-10 em {ano_selecionado}", x_title="Número de Internações", y_title="")
            st.plotly_chart(fig_rank, use_container_width=True)
            
            # Tabela ordenada
            st.markdown("#### Detalhamento dos Registros")
            df_ranking_tabela = df_ranking.sort_values(by=ano_selecionado, ascending=False)
            df_ranking_tabela["Percentual (%)"] = (df_ranking_tabela[ano_selecionado] / df_ranking_tabela[ano_selecionado].sum() * 100).round(2)
            st.dataframe(
                df_ranking_tabela.rename(columns={"capitulo_cid": "Capitulo CID-10", ano_selecionado: "Internações"}), 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Nenhum registro encontrado para o filtro digitado.")

    with tab_tendencia:
        st.markdown("### Evolução Temporal por Capitulo CID-10")
        
        capitulos_disponiveis = df_filtrado_busca["capitulo_cid"].unique()
        top_3_causas = df_filtrado_busca.sort_values(by="Total_Causa", ascending=False).head(3)["capitulo_cid"].tolist()
        
        capitulos_selecionados = st.multiselect(
            "Selecione os Capitulos CID-10 para comparar a evolucao", 
            options=capitulos_disponiveis,
            default=top_3_causas if len(top_3_causas) > 0 else (capitulos_disponiveis[:3] if len(capitulos_disponiveis) >= 3 else list(capitulos_disponiveis))
        )
        
        if len(capitulos_selecionados) > 0:
            df_filtrado_grafico = df_filtrado_busca[df_filtrado_busca["capitulo_cid"].isin(capitulos_selecionados)].copy()
            
            df_melted = df_filtrado_grafico.melt(
                id_vars=["capitulo_cid"],
                value_vars=anos,
                var_name="Ano",
                value_name="Internações"
            )
            
            fig_trend = px.line(
                df_melted,
                x="Ano",
                y="Internações",
                color="capitulo_cid",
                title="Evolução Temporal das Internações",
                markers=True,
                color_discrete_sequence=colors["categorical"]
            )
            aplicar_estilo_layout(fig_trend, title="Evolução Temporal das Internações por CID-10", x_title="Ano", y_title="Internações")
            st.plotly_chart(fig_trend, use_container_width=True)
            
            st.markdown("#### Tabela Comparativa de Tendências")
            df_pivot = df_filtrado_grafico[["capitulo_cid"] + anos]
            st.dataframe(df_pivot, use_container_width=True, hide_index=True)
        else:
            st.info("Selecione pelo menos um capitulo do CID-10 para ver a evolucao temporal.")
            
except Exception as e:
    st.error(f"Erro ao processar as visualizacoes de internacoes: {e}")
