import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# coloca a pasta raiz no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.charts import injetar_custom_css, aplicar_estilo_layout, obter_paleta_cores
from src.api_client import obter_estados_municipios, consultar_cnes_leitos

# configuracao da pagina
st.set_page_config(page_title="CNES - Leitos Hospitalares | Painel DATASUS", layout="wide")
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
st.title("Leitos Hospitalares (CNES)")
st.markdown(
    f"""
    <p class="text-secondary mb-4" style="font-size: 14px; margin-top: -10px;">
        Capacidade instalada de internação — <b>{st.session_state.mun_selecionado['nome']} ({st.session_state.uf_selecionada})</b>
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# Carrega os dados de leitos
try:
    with st.spinner("Buscando leitos no banco de dados..."):
        df = consultar_cnes_leitos(st.session_state.mun_selecionado['id'])
except Exception as e:
    st.error(f"Não foi possível obter os dados de leitos do CNES: {e}")
    df = pd.DataFrame()

if df.empty:
    st.warning("Nenhum leito encontrado no CNES para esta localidade.")
    st.stop()

# Converte para numérico e limpa
for col in ["leitos_existentes", "leitos_contratados", "leitos_sus"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
df["descricao_tipo_leito"] = df["descricao_tipo_leito"].fillna("Outros").astype(str)
df["nome_fantasia"] = df["nome_fantasia"].fillna("").astype(str)

# Filtro por tipo de leito
tipos = sorted(df["descricao_tipo_leito"].unique())
tipos_sel = st.sidebar.multiselect("Tipo de Leito", options=tipos, default=tipos)
df_filt = df[df["descricao_tipo_leito"].isin(tipos_sel)]

# KPIs
total_leitos = int(df_filt["leitos_existentes"].sum())
leitos_sus = int(df_filt["leitos_sus"].sum())
leitos_contr = int(df_filt["leitos_contratados"].sum())
hospitais_com_leito = df_filt["codigo_cnes"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Leitos Existentes", f"{total_leitos:,}".replace(",", "."))
c2.metric("Leitos SUS", f"{leitos_sus:,}".replace(",", "."))
c3.metric("Leitos Contratados", f"{leitos_contr:,}".replace(",", "."))
c4.metric("Estabelecimentos com Leito", hospitais_com_leito)

st.markdown("---")

# Gráficos
col1, col2 = st.columns(2)
with col1:
    df_tipo = df_filt.groupby("descricao_tipo_leito")[["leitos_existentes", "leitos_sus"]].sum().reset_index().sort_values("leitos_existentes", ascending=False)
    fig = px.bar(df_tipo, x="descricao_tipo_leito", y=["leitos_existentes", "leitos_sus"], barmode="group",
                 title="Leitos por Tipo (Total x SUS)", color_discrete_sequence=[colors["internacoes"], colors["nascimentos_emerald"]],
                 labels={"value": "Leitos", "variable": "Origem"})
    aplicar_estilo_layout(fig, "Leitos por Tipo de Especialidade", x_title="", y_title="Leitos")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_hosp = df_filt.groupby("nome_fantasia")["leitos_existentes"].sum().reset_index().sort_values("leitos_existentes", ascending=False).head(12)
    fig2 = px.bar(df_hosp, x="leitos_existentes", y="nome_fantasia", orientation="h", title="Top Estabelecimentos por Leitos", color_discrete_sequence=[colors["nascimentos_amber"]])
    aplicar_estilo_layout(fig2, "Estabelecimentos com Mais Leitos", x_title="Leitos", y_title="")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Tabela detalhada
st.subheader("Detalhamento por Estabelecimento")
detalhe = df_filt[["codigo_cnes", "nome_fantasia", "descricao_tipo_leito", "leitos_existentes", "leitos_contratados", "leitos_sus"]].copy()
detalhe.columns = ["CNES", "Estabelecimento", "Tipo de Leito", "Existentes", "Contratados", "SUS"]
detalhe = detalhe.sort_values(["CNES", "Tipo de Leito"]).reset_index(drop=True)

st.dataframe(detalhe, use_container_width=True, hide_index=True)
st.caption(f"Total de {len(detalhe)} registros de leitos cadastrados no CNES.")
