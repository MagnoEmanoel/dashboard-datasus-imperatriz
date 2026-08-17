import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# coloca a pasta raiz no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.charts import injetar_custom_css, aplicar_estilo_layout, obter_paleta_cores
from src.api_client import obter_estados_municipios, consultar_cnes_subtipos

# configuracao da pagina
st.set_page_config(page_title="CNES - Unidades Especializadas | Painel DATASUS", layout="wide")
st.markdown(injetar_custom_css(), unsafe_allow_html=True)

colors = obter_paleta_cores()

# Carrega Estados e Municípios do IBGE
ufs, mun_map = obter_estados_municipios()

# Inicializa o session_state para estado e municipio se não existirem
if 'uf_selecionada' not in st.session_state:
    st.session_state.uf_selecionada = "MA"
if 'mun_selecionado' not in st.session_state:
    st.session_state.mun_selecionado = {"id": "210530", "nome": "Imperatriz"}

# Barra lateral
with st.sidebar:
    st.markdown("### Filtros Globais")
    st.markdown("---")

    uf_sel = st.selectbox("Estado (UF)", options=ufs, index=ufs.index(st.session_state.uf_selecionada) if st.session_state.uf_selecionada in ufs else ufs.index('MA'))
    st.session_state.uf_selecionada = uf_sel

    muns_uf = mun_map.get(uf_sel, [{"id": "210530", "nome": "Imperatriz"}])
    mun_nomes = [m["nome"] for m in muns_uf]

    current_mun_nome = st.session_state.mun_selecionado.get('nome', '')
    mun_index = mun_nomes.index(current_mun_nome) if current_mun_nome in mun_nomes else 0

    mun_nome_sel = st.selectbox("Município", options=mun_nomes, index=mun_index)
    mun_obj_sel = next((m for m in muns_uf if m["nome"] == mun_nome_sel), muns_uf[0])
    st.session_state.mun_selecionado = mun_obj_sel

    st.markdown("---")
    st.markdown(f"**Código IBGE:** {mun_obj_sel['id']}")
    st.markdown("---")

# Título
st.title("Unidades Especializadas (CNES)")
st.markdown(
    f"""
    <p class="text-secondary mb-4" style="font-size: 14px; margin-top: -10px;">
        Subtipos de unidades: CAPS, UPA, Laboratórios, CASAI, CER e outros — <b>{st.session_state.mun_selecionado['nome']} ({st.session_state.uf_selecionada})</b>
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# Carrega os dados de subtipos
try:
    with st.spinner("Buscando unidades especializadas no banco de dados..."):
        df = consultar_cnes_subtipos(st.session_state.mun_selecionado['id'])
except Exception as e:
    st.error(f"Não foi possível obter os dados de subtipos do CNES: {e}")
    df = pd.DataFrame()

if df.empty:
    st.warning("Nenhum subtipo de unidade encontrado no CNES para esta localidade.")
    st.stop()

for col in df.columns:
    df[col] = df[col].fillna("Não Informado").astype(str)

# Filtro por subtipo
subtipos = sorted([s for s in df["descricao_subtipo"].unique() if s and s != "OUTROS"])
subtipos_sel = st.sidebar.multiselect("Subtipo de Unidade", options=subtipos, default=subtipos)

df_filt = df[df["descricao_subtipo"].isin(subtipos_sel)]

# KPIs
total_unidades = df_filt["codigo_cnes"].nunique()
total_vinculos = len(df_filt)
n_subtipos = df_filt["descricao_subtipo"].nunique()

c1, c2, c3 = st.columns(3)
c1.metric("Unidades Únicas", total_unidades)
c2.metric("Vínculos de Subtipo", total_vinculos)
c3.metric("Subtipos Distintos", n_subtipos)

st.markdown("---")

# Gráficos
col1, col2 = st.columns(2)
with col1:
    df_sub = df_filt.groupby("descricao_subtipo")["codigo_cnes"].nunique().reset_index(name="Unidades").sort_values("Unidades", ascending=False)
    fig = px.bar(df_sub, x="Unidades", y="descricao_subtipo", orientation="h", title="Unidades por Subtipo", color_discrete_sequence=[colors["internacoes"]])
    aplicar_estilo_layout(fig, "Quantidade de Unidades por Subtipo", x_title="Unidades", y_title="")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_tipo = df_filt.groupby("descricao_tipo_unidade")["codigo_cnes"].nunique().reset_index(name="Unidades").sort_values("Unidades", ascending=False)
    fig2 = px.pie(df_tipo, names="descricao_tipo_unidade", values="Unidades", hole=0.45, title="Distribuição por Tipo de Unidade", color_discrete_sequence=colors["categorical"])
    aplicar_estilo_layout(fig2, "Distribuição por Tipo de Unidade")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Tabela
st.subheader("Relação de Unidades Especializadas")
tabela = df_filt[["codigo_cnes", "nome_fantasia", "descricao_tipo_unidade", "descricao_subtipo"]].copy()
tabela.columns = ["CNES", "Nome Fantasia", "Tipo de Unidade", "Subtipo"]
tabela = tabela.sort_values(["Subtipo", "Nome Fantasia"]).reset_index(drop=True)

st.dataframe(tabela, use_container_width=True, hide_index=True)
st.caption(f"Total de {len(tabela)} registros de subtipos cadastrados no CNES.")
