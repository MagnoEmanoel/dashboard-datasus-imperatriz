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
st.set_page_config(page_title="Perfil de Nascimentos | DATASUS", layout="wide")
st.markdown(injetar_custom_css(), unsafe_allow_html=True)

# cores e conexao com o banco
colors = obter_paleta_cores()
_, db_type = criar_engine()

# titulo
st.title("Perfil de Nascimentos")
st.caption(f"Fonte: SINASC (Sistema de Informação sobre Nascidos Vivos) / DATASUS | Banco de dados: {db_type.upper()}")
st.markdown("---")

try:
    df_sinasc = carregar_tabela("sinasc_nascimentos")
except Exception as e:
    st.error("Erro ao conectar ao banco de dados ou carregar tabelas de nascimentos. Verifique se realizou a ingestão de dados.")
    st.info("Execute: python src/ingest.py no terminal.")
    st.stop()

try:
    anos = [c for c in df_sinasc.columns if c.isdigit()]
    
    # Seletor interativo de ano no topo (Controle de tempo minimalista)
    st.markdown("### Selecione o Período de Análise")
    ano_sel = st.selectbox("Selecione o ano para filtrar os indicadores", options=sorted(anos, reverse=True))
    
    # Filtrar dados para o ano selecionado
    df_ano = df_sinasc[["faixa_etaria_mae", ano_sel]].copy()
    df_ano = df_ano.rename(columns={ano_sel: "nascidos"})
    
    # Calcular métricas dinâmicas para o ano selecionado (Igual a NascimentosView.tsx)
    total_nascidos_ano = int(df_ano["nascidos"].sum())
    
    # Gravidez na adolescência (<20 anos)
    faixas_adolescentes = ["10 a 14 anos", "15 a 19 anos"]
    total_adolescentes = int(df_ano[df_ano["faixa_etaria_mae"].isin(faixas_adolescentes)]["nascidos"].sum())
    pct_adolescentes = (total_adolescentes / total_nascidos_ano * 100) if total_nascidos_ano > 0 else 0
    
    # Maternidade tardia (35+ anos)
    faixas_maduras = ["35 a 39 anos", "40 a 44 anos", "45 a 49 anos", "50 a 54 anos"]
    total_maduras = int(df_ano[df_ano["faixa_etaria_mae"].isin(faixas_maduras)]["nascidos"].sum())
    pct_maduras = (total_maduras / total_nascidos_ano * 100) if total_nascidos_ano > 0 else 0

    # Grid de KPIs dinâmicos do Bootstrap
    st.markdown(
        f"""
<div class="row g-4 mb-4">
<!-- KPI 1: Nascidos Vivos no Ano -->
<div class="col-12 col-md-4">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['nascimentos_emerald']} !important; border-radius: 8px; background-color: #ffffff;">
<div class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em; margin-bottom: 8px;">Nascidos Vivos no Ano ({ano_sel})</div>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{total_nascidos_ano:,}</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">Total bruto acumulado no banco local SINASC</div>
</div>
</div>

<!-- KPI 2: Maternidade na Adolescência -->
<div class="col-12 col-md-4">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['mortalidade_infantil']} !important; border-radius: 8px; background-color: #ffffff;">
<div class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em; margin-bottom: 8px;">Maternidade na Adolescencia (&lt;20 anos)</div>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{total_adolescentes:,}</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">Corresponde a <b>{pct_adolescentes:.1f}%</b> das gestacoes em {ano_sel}</div>
</div>
</div>

<!-- KPI 3: Maternidade Tardia -->
<div class="col-12 col-md-4">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['nascimentos_amber']} !important; border-radius: 8px; background-color: #ffffff;">
<div class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em; margin-bottom: 8px;">Maternidade Tardia (35+ anos)</div>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{total_maduras:,}</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">Corresponde a <b>{pct_maduras:.1f}%</b> das gestacoes em {ano_sel}</div>
</div>
</div>
</div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # Seções de Gráficos e Tabelas
    col_donut, col_table = st.columns([1, 1])
    
    with col_donut:
        st.markdown(f"### Perfil de Idade das Maes em {ano_sel}")
        
        # Donut Chart
        fig_donut = px.pie(
            df_ano,
            names="faixa_etaria_mae",
            values="nascidos",
            hole=0.45,
            color_discrete_sequence=colors["categorical"]
        )
        
        fig_donut.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hoverinfo="label+value+percent"
        )
        
        fig_donut.update_layout(
            annotations=[
                dict(
                    text="Idade<br>Materna",
                    x=0.5, y=0.5,
                    font_size=13,
                    font_family="Inter, sans-serif",
                    showarrow=False,
                    font_color=colors["text_main"]
                )
            ]
        )
        
        aplicar_estilo_layout(fig_donut, title=f"Distribuicao Proporcional - Ano {ano_sel}")
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col_table:
        st.markdown("### Detalhamento da Faixa Etaria")
        
        df_ano_exib = df_ano.copy()
        df_ano_exib["proporcao"] = (df_ano_exib["nascidos"] / total_nascidos_ano * 100) if total_nascidos_ano > 0 else 0
        
        # Desenhar a tabela com dados ordenados
        df_ano_exib = df_ano_exib.sort_values(by="nascidos", ascending=False)
        
        # Tabela minimalista
        st.dataframe(
            df_ano_exib.rename(columns={"faixa_etaria_mae": "Faixa Etaria da Mae", "nascidos": "Nascidos Vivos", "proporcao": "Proporcao (%)"}),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")
    st.markdown("### Serie Historica de Nascimentos")
    
    # Gráfico de linhas para tendência temporal (Tudo integrado)
    df_melted = df_sinasc.melt(
        id_vars=["faixa_etaria_mae"],
        value_vars=anos,
        var_name="Ano",
        value_name="Nascimentos"
    )
    
    fig_lin = px.line(
        df_melted,
        x="Ano",
        y="Nascimentos",
        color="faixa_etaria_mae",
        title="Serie Historica por Faixa Etaria",
        markers=True,
        color_discrete_sequence=colors["categorical"]
    )
    aplicar_estilo_layout(fig_lin, title="Evolução Temporal dos Nascimentos (2020-2024)", x_title="Ano", y_title="Nascidos Vivos")
    st.plotly_chart(fig_lin, use_container_width=True)
    
    st.markdown("""
> **Nota Epidemiologica**: O monitoramento constante das gestacoes em adolescentes (10-19 anos) 
> e central para as equipes de Saúde da Familia (eSF). Uma tendencia de queda nesta faixa sugere eficacia de programas
> de planejamento familiar e de educacao sexual nas escolas. Em paralelo, o crescimento de partos em mulheres com
> mais de 35 anos impoe um planejamento de pré-natal de alto risco mais estruturado.
    """)
        
except Exception as e:
    st.error(f"Erro ao processar os dados do SINASC: {e}")
