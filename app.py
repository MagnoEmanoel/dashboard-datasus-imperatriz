import streamlit as st
import sys
import os

# coloca a pasta raiz no path pra achar os modulos
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.charts import injetar_custom_css, obter_paleta_cores
from src.database import carregar_tabela, criar_engine

# configuracao da pagina do Streamlit
st.set_page_config(
    page_title="Painel de Saude - Imperatriz MA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# aplica o CSS customizado e carrega as cores
st.markdown(injetar_custom_css(), unsafe_allow_html=True)
colors = obter_paleta_cores()

# menu lateral com informacoes do projeto
with st.sidebar:
    st.markdown("### Painel de Saude")
    st.markdown("---")
    st.markdown("**Municipio:** Imperatriz - MA")
    st.markdown("**IBGE:** 210530")
    st.markdown("**Periodo Analisado:** 2020 - 2026")
    st.markdown("---")
    _, db_type = criar_engine()
    st.markdown(f"Conexao ativa: **{db_type.upper()}**")

# titulo principal da pagina
st.title("Painel de Saude Publica")
st.markdown(
    """
    <p class="text-secondary mb-4" style="font-size: 14px; margin-top: -10px;">
        Atencao Primaria a Saude — Municipio de Imperatriz, Maranhao
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# tenta puxar os dados do banco pra mostrar os numeros
total_obitos = 0
total_internacoes = 0
total_nascimentos = 0
vacinacao_media = 0
dados_prontos = False

try:
    df_ad = carregar_tabela("obitos_adultos")
    df_inf = carregar_tabela("obitos_infantis")
    anos_ad = [c for c in df_ad.columns if c.isdigit()]
    anos_inf = [c for c in df_inf.columns if c.isdigit()]
    
    total_obitos = int(df_ad[anos_ad].sum().sum() + df_inf[anos_inf].sum().sum())
    
    df_int = carregar_tabela("internacoes")
    anos_int = [c for c in df_int.columns if c.isdigit()]
    total_internacoes = int(df_int[anos_int].sum().sum())
    
    df_nas = carregar_tabela("sinasc_nascimentos")
    anos_nas = [c for c in df_nas.columns if c.isdigit()]
    total_nascimentos = int(df_nas[anos_nas].sum().sum())
    
    df_vac = carregar_tabela("vacinacao_cobertura")
    if len(df_vac) > 0:
        vacinas = [c for c in df_vac.columns if c != "ano"]
        ultimo_ano_df = df_vac.sort_values(by="ano", ascending=False).iloc[0]
        vacinacao_media = float(ultimo_ano_df[vacinas].mean())
        
    dados_prontos = True
except Exception as e:
    dados_prontos = False

if dados_prontos:
    # monta os 4 cards com os numeros principais
    st.markdown(
        f"""
<div class="row g-4 mb-5">
<!-- Card 1: Óbitos Evitáveis -->
<div class="col-12 col-md-6 col-lg-3">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['mortalidade_infantil']} !important; border-radius: 8px; background-color: #ffffff;">
<div class="d-flex justify-content-between align-items-center mb-3">
<span class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em;">Obitos Evitaveis</span>
</div>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{total_obitos:,}</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">SIM (2020 - 2024 acumulados)</div>
</div>
</div>

<!-- Card 2: Internações -->
<div class="col-12 col-md-6 col-lg-3">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['internacoes']} !important; border-radius: 8px; background-color: #ffffff;">
<div class="d-flex justify-content-between align-items-center mb-3">
<span class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em;">Internacoes</span>
</div>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{total_internacoes:,}</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">SIH (2020 - 2026 acumulados)</div>
</div>
</div>

<!-- Card 3: Nascidos Vivos -->
<div class="col-12 col-md-6 col-lg-3">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['nascimentos_emerald']} !important; border-radius: 8px; background-color: #ffffff;">
<div class="d-flex justify-content-between align-items-center mb-3">
<span class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em;">Nascidos Vivos</span>
</div>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{total_nascimentos:,}</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">SINASC (2020 - 2024 acumulados)</div>
</div>
</div>

<!-- Card 4: Cobertura Vacinal -->
<div class="col-12 col-md-6 col-lg-3">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['vacinacao']} !important; border-radius: 8px; background-color: #ffffff;">
<div class="d-flex justify-content-between align-items-center mb-3">
<span class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em;">Cobertura Vacinal Geral</span>
</div>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{vacinacao_media:.2f}%</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">SI-PNI (Media de imunizacao local)</div>
</div>
</div>
</div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
else:
    st.warning("A base de dados ainda nao foi populada. Por favor, execute a ingestao de dados no terminal para visualizar os KPIs.")
    st.info("Para popular: python src/ingest.py")
    st.markdown("---")

# secao com informacoes sobre o painel e o municipio
st.markdown(
    f"""
<div class="row g-4">
<!-- Coluna Esquerda: Sobre o Painel -->
<div class="col-12 col-lg-8">
<div class="card p-4 border-light shadow-sm h-100" style="background-color: #ffffff; border-radius: 8px;">
<div class="border-bottom border-light pb-3 mb-3">
<h5 class="text-dark font-sans fw-bold mb-0">Sobre este Painel</h5>
</div>
<p class="text-secondary leading-relaxed font-sans mb-4" style="font-size: 13px;">
Acompanhe a consolidacao historica dos indicadores publicos da saude primaria de Imperatriz (MA). Este painel foi construido de forma limpa e objetiva para facilitar a analise dos gestores e da equipe cientifica. Os dados provem das fontes unificadas de dados abertos do DATASUS (Ministerio da Saude):
</p>

<div class="row g-3">
<div class="col-12 col-md-6">
<div class="p-3 bg-light border border-light rounded" style="border-radius: 6px;">
<div class="text-xs fw-bold text-dark font-sans mb-1" style="font-size: 12px;">Mortalidade Evitavel</div>
<p class="text-secondary mb-0 font-sans" style="font-size: 11px; line-height: 1.5;">
Consolidação contínua do SIM (Sistema de Informação sobre Mortalidade), tratando de causas controláveis através de ações corretas preventivas locais.
</p>
</div>
</div>
<div class="col-12 col-md-6">
<div class="p-3 bg-light border border-light rounded" style="border-radius: 6px;">
<div class="text-xs fw-bold text-dark font-sans mb-1" style="font-size: 12px;">Internacoes Hospitalares</div>
<p class="text-secondary mb-0 font-sans" style="font-size: 11px; line-height: 1.5;">
Métricas originadas do SIH (Sistema de Informações Hospitalares) organizadas por capítulos da Classificação Internacional de Doenças (CID-10).
</p>
</div>
</div>
<div class="col-12 col-md-6">
<div class="p-3 bg-light border border-light rounded" style="border-radius: 6px;">
<div class="text-xs fw-bold text-dark font-sans mb-1" style="font-size: 12px;">Nascidos Vivos</div>
<p class="text-secondary mb-0 font-sans" style="font-size: 11px; line-height: 1.5;">
Estatísticas de natalidade do SINASC, divididas pelo perfil de faixas etárias maternas para monitoramento de risco social.
</p>
</div>
</div>
<div class="col-12 col-md-6">
<div class="p-3 bg-light border border-light rounded" style="border-radius: 6px;">
<div class="text-xs fw-bold text-dark font-sans mb-1" style="font-size: 12px;">Cobertura Vacinal</div>
<p class="text-secondary mb-0 font-sans" style="font-size: 11px; line-height: 1.5;">
Acompanhamento e monitoramento das taxas históricas consolidadas pelo SI-PNI frente à meta preconizada de imunidade coletiva regional.
</p>
</div>
</div>
</div>
</div>
</div>

<!-- Coluna Direita: Informações Municipais -->
<div class="col-12 col-lg-4">
<div class="card p-4 border-light shadow-sm h-100 d-flex flex-column justify-content-between" style="background-color: #ffffff; border-radius: 8px;">
<div>
<div class="border-bottom border-light pb-3 mb-3">
<h5 class="text-dark font-sans fw-bold mb-0">Imperatriz – MA</h5>
</div>
<p class="text-secondary leading-relaxed font-sans mb-4" style="font-size: 12px;">
Considerada o "Portal da Amazônia" e o segundo município mais populoso do estado. Imperatriz funciona como um decisivo polo regional de assistência de saúde secundária e terciária para municípios limítrofes do sul do Maranhão, Tocantins e Pará.
</p>

<div class="border-top border-light pt-3 space-y-2 font-sans" style="font-size: 11px;">
<div class="d-flex justify-content-between text-secondary mb-2">
<span>Codigo IBGE</span>
<span class="font-monospace text-dark fw-bold">210530</span>
</div>
<div class="d-flex justify-content-between text-secondary mb-2">
<span>Macro-regiao</span>
<span class="text-dark fw-bold">Sul do Maranhao</span>
</div>
<div class="d-flex justify-content-between text-secondary mb-0">
<span>Populacao Estimada</span>
<span class="font-monospace text-dark fw-bold">~273.000 hab.</span>
</div>
</div>
</div>

<div class="mt-4 p-2 bg-light border border-light rounded d-flex align-items-center gap-2" style="border-radius: 6px;">
<div class="rounded-circle bg-dark" style="width: 6px; height: 6px;"></div>
<span class="text-uppercase text-dark fw-bold font-sans" style="font-size: 9px; letter-spacing: 0.08em;">
Conexao Ativa: DATASUS ({db_type.upper()})
</span>
</div>
</div>
</div>
</div>

<!-- Footer -->
<p class="text-center text-secondary mt-5 border-top border-light pt-4 font-sans" style="font-size: 10px; max-w: 700px; margin: 30px auto 0;">
Fonte consolidada oficial do DATASUS / Ministério da Saúde. Os indicadores descritos refletem o banco local tratado conforme diretrizes de interoperabilidade do SUS.
</p>
""",
    unsafe_allow_html=True
)
