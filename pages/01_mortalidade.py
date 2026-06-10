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
st.set_page_config(page_title="Mortalidade Evitavel | DATASUS", layout="wide")
st.markdown(injetar_custom_css(), unsafe_allow_html=True)

# cores e conexao com o banco
colors = obter_paleta_cores()
_, db_type = criar_engine()

# titulo
st.title("Mortalidade Evitavel")
st.caption(f"Fonte: SIM (Sistema de Informacao sobre Mortalidade) / DATASUS | Banco de dados: {db_type.upper()}")
st.markdown("---")

try:
    df_ad = carregar_tabela("obitos_adultos")
    df_inf = carregar_tabela("obitos_infantis")
except Exception as e:
    st.error("Erro ao conectar ao banco de dados ou carregar tabelas de obitos. Verifique se realizou a ingestao de dados.")
    st.info("Execute: python src/ingest.py no terminal.")
    st.stop()

# filtros na barra lateral
st.sidebar.markdown("### Filtros - Mortalidade")
grupo_analise = st.sidebar.selectbox("Selecione o grupo etario", ["Ambos (Resumo)", "Infantil (< 5 anos)", "Jovem e Adulto (5 a 74 anos)"])

if grupo_analise == "Ambos (Resumo)":
    st.subheader("Visao Geral - Mortalidade Evitavel em Imperatriz MA")
    
    # calcula os totais pra mostrar nos cards
    anos = [c for c in df_ad.columns if c.isdigit()]
    total_ad = df_ad[anos].sum().sum()
    total_inf = df_inf[anos].sum().sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: {colors['mortalidade_infantil']};">
                <div class="metric-title">Obitos Totais Analisados</div>
                <div class="metric-value">{int(total_ad + total_inf):,}</div>
                <div class="metric-subtitle">Mortalidade Evitavel Acumulada (2020-2024)</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: {colors['mortalidade_adulto']};">
                <div class="metric-title">Obitos Infantil (<5 anos)</div>
                <div class="metric-value">{int(total_inf):,}</div>
                <div class="metric-subtitle">Representa {total_inf / (total_ad + total_inf) * 100:.1f}% do total de obitos</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: {colors['nascimentos_amber']};">
                <div class="metric-title">Obitos Jovem/Adulto (5-74)</div>
                <div class="metric-value">{int(total_ad):,}</div>
                <div class="metric-subtitle">Representa {total_ad / (total_ad + total_inf) * 100:.1f}% do total de obitos</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown("### Comparacao Temporal de Tendencias")
    
    # junta os dados de ambos os grupos por ano
    obitos_ad_ano = df_ad[anos].sum()
    obitos_inf_ano = df_inf[anos].sum()
    
    df_tendencia = pd.DataFrame({
        "Ano": anos,
        "Jovem/Adulto (5 a 74 anos)": obitos_ad_ano.values,
        "Infantil (< 5 anos)": obitos_inf_ano.values,
        "Total": (obitos_ad_ano + obitos_inf_ano).values
    })
    
    # grafico de linhas comparando adulto vs infantil
    fig = px.line(
        df_tendencia, 
        x="Ano", 
        y=["Jovem/Adulto (5 a 74 anos)", "Infantil (< 5 anos)"],
        title="Evolucao de Obitos Evitaveis por Grupo Etario",
        markers=True,
        color_discrete_map={
            "Jovem/Adulto (5 a 74 anos)": colors["mortalidade_adulto"],
            "Infantil (< 5 anos)": colors["mortalidade_infantil"]
        }
    )
    aplicar_estilo_layout(fig, title="Evolucao de Obitos Evitaveis por Grupo Etario", x_title="Ano", y_title="Quantidade de Obitos")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Detalhes das Series Temporais")
    st.dataframe(df_tendencia, use_container_width=True, hide_index=True)

elif grupo_analise == "Infantil (< 5 anos)":
    st.subheader("Indicadores de Mortalidade Infantil Evitavel (< 5 anos)")
    
    anos = [c for c in df_inf.columns if c.isdigit()]
    total_inf = df_inf[anos].sum().sum()
    media_anual = df_inf[anos].mean(axis=1).values[0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: {colors['mortalidade_infantil']};">
                <div class="metric-title">Obitos Infantil Acumulado</div>
                <div class="metric-value">{int(total_inf)}</div>
                <div class="metric-subtitle">Total de obitos evitaveis menores de 5 anos (2020-2024)</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: {colors['nascimentos_emerald']};">
                <div class="metric-title">Media de Obitos/Ano</div>
                <div class="metric-value">{media_anual:.1f}</div>
                <div class="metric-subtitle">Media anual no periodo analisado</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown("### Evolucao da Mortalidade Infantil Evitavel")
    
    df_plot_inf = pd.DataFrame({
        "Ano": anos,
        "Óbitos": df_inf[anos].values[0]
    })
    
    fig_inf = px.bar(
        df_plot_inf,
        x="Ano",
        y="Óbitos",
        title="Numero de Obitos Evitaveis (<5 anos) por Ano",
        text="Óbitos",
        color_discrete_sequence=[colors["mortalidade_infantil"]]
    )
    fig_inf.update_traces(textposition='inside')
    aplicar_estilo_layout(fig_inf, title="Evolucao de Obitos Evitaveis (<5 anos) por Ano", x_title="Ano", y_title="Obitos")
    st.plotly_chart(fig_inf, use_container_width=True)
    
    st.markdown("""
> **Nota Metodologica**: A mortalidade em menores de 5 anos e um importante indicador de desenvolvimento social e qualidade da 
> Atencao Basica de saude. Casos evitaveis geralmente estao relacionados a deficiencias no acompanhamento 
> pre-natal, assistencia ao parto e puerperio e cobertura vacinal na primeira infancia.
    """)

elif grupo_analise == "Jovem e Adulto (5 a 74 anos)":
    st.subheader("Analise Detalhada - Mortalidade Jovem e Adulto (5 a 74 anos)")
    
    df_ad["is_grupo"] = df_ad["causa"].apply(lambda x: not x.startswith("..") and x[0].isdigit())
    df_ad["is_subgrupo"] = df_ad["causa"].apply(lambda x: x.startswith(".."))
    
    df_grupos = df_ad[df_ad["is_grupo"]].copy()
    df_subgrupos = df_ad[df_ad["is_subgrupo"]].copy()
    
    df_grupos["causa_limpa"] = df_grupos["causa"].apply(lambda x: x.split(".", 1)[-1].strip() if "." in x else x)
    df_subgrupos["causa_limpa"] = df_subgrupos["causa"].apply(lambda x: x.replace("..", "").strip())
    
    anos = [c for c in df_ad.columns if c.isdigit()]
    total_ad = df_ad[df_ad["causa"].str.strip() == "1. Causas evitáveis"][anos].sum().sum()
    if total_ad == 0:
        grupos_evitaveis = ["1.1. Reduzíveis pelas ações de imunoprevenção", 
                            "1.2. Reduz ações prom prev contr atenç doenç infec", 
                            "1.3. Reduz ações prom prev contr atenç doe ñ trans", 
                            "1.4. Reduz ações prev contr atenção causas matern", 
                            "1.5. Reduz ações prom prev atenç causas externas"]
        total_ad = df_ad[df_ad["causa"].isin(grupos_evitaveis)][anos].sum().sum()

    st.markdown(
        f"""
        <div class="metric-card" style="border-left-color: {colors['mortalidade_adulto']}; margin-bottom: 20px;">
            <div class="metric-title">Obitos Evitaveis Acumulados (5 a 74 anos)</div>
            <div class="metric-value">{int(total_ad):,}</div>
            <div class="metric-subtitle">Total de mortes decorrentes de causas evitaveis (2020-2024)</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    tab1, tab2 = st.tabs(["Grandes Grupos de Causa", "Causas Especificas (CID)"])
    
    with tab1:
        st.markdown("### Obitos por Grandes Grupos de Causa Evitavel")
        
        grupos_interesse = [
            "1.1. Reduzíveis pelas ações de imunoprevenção", 
            "1.2. Reduz ações prom prev contr atenç doenç infec", 
            "1.3. Reduz ações prom prev contr atenç doe ñ trans", 
            "1.4. Reduz ações prev contr atenção causas matern", 
            "1.5. Reduz ações prom prev atenç causas externas"
        ]
        
        df_principais = df_grupos[df_grupos["causa"].isin(grupos_interesse)].copy()
        
        if len(df_principais) > 0:
            df_principais["Total_Acumulado"] = df_principais[anos].sum(axis=1)
            df_principais = df_principais.sort_values(by="Total_Acumulado", ascending=True)
            
            fig_grupos = px.bar(
                df_principais,
                x="Total_Acumulado",
                y="causa_limpa",
                orientation="h",
                title="Total de Obitos por Grupo de Causa (2020-2024)",
                color_discrete_sequence=[colors["mortalidade_adulto"]],
                labels={"causa_limpa": "Grupo de Causa", "Total_Acumulado": "Obitos Acumulados"}
            )
            aplicar_estilo_layout(fig_grupos, title="Ranking dos Grupos de Causa Evitavel", x_title="Obitos", y_title="")
            st.plotly_chart(fig_grupos, use_container_width=True)
            
            df_melted = df_principais.melt(
                id_vars=["causa_limpa"], 
                value_vars=anos, 
                var_name="Ano", 
                value_name="Obitos"
            )
            
            fig_lin_grupos = px.line(
                df_melted,
                x="Ano",
                y="Obitos",
                color="causa_limpa",
                title="Evolucao Temporal dos Obitos por Grupo de Causa",
                markers=True,
                color_discrete_sequence=colors["categorical"]
            )
            aplicar_estilo_layout(fig_lin_grupos, title="Tendencia dos Grupos de Causas Evitaveis", x_title="Ano", y_title="Obitos")
            st.plotly_chart(fig_lin_grupos, use_container_width=True)
            
        else:
            st.warning("Não foi possível carregar os grandes grupos de óbitos evitáveis.")

    with tab2:
        st.markdown("### Principais Causas Especificas de Obitos Evitaveis")
        
        df_subgrupos["Total_Acumulado"] = df_subgrupos[anos].sum(axis=1)
        top_causas = df_subgrupos.sort_values(by="Total_Acumulado", ascending=True).head(15)
        
        fig_top = px.bar(
            top_causas,
            x="Total_Acumulado",
            y="causa_limpa",
            orientation="h",
            title="Top 15 Causas Especificas de Mortes Evitaveis (2020-2024)",
            color_discrete_sequence=[colors["mortalidade_adulto"]],
            labels={"causa_limpa": "Causa Especifica", "Total_Acumulado": "Obitos"}
        )
        aplicar_estilo_layout(fig_top, title="Top 15 Causas Especificas de Mortes Evitaveis", x_title="Obitos Acumulados", y_title="")
        st.plotly_chart(fig_top, use_container_width=True)
        
        st.markdown("#### Detalhar Tendencia de uma Causa Especifica")
        causa_select = st.selectbox("Selecione a Causa Especifica para analise", df_subgrupos["causa_limpa"].unique())
        
        df_causa_sel = df_subgrupos[df_subgrupos["causa_limpa"] == causa_select]
        if len(df_causa_sel) > 0:
            df_causa_trend = pd.DataFrame({
                "Ano": anos,
                "Óbitos": df_causa_sel[anos].values[0]
            })
            
            fig_causa_sel = px.line(
                df_causa_trend,
                x="Ano",
                y="Óbitos",
                title=f"Evolucao Temporal: {causa_select}",
                markers=True,
                color_discrete_sequence=[colors["mortalidade_adulto"]]
            )
            aplicar_estilo_layout(fig_causa_sel, title=f"Historico de Obitos: {causa_select}", x_title="Ano", y_title="Obitos")
            st.plotly_chart(fig_causa_sel, use_container_width=True)
            
            st.dataframe(df_causa_sel[["causa_limpa"] + anos], hide_index=True, use_container_width=True)
