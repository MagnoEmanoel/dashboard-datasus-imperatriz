import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# coloca a pasta raiz no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.charts import injetar_custom_css, aplicar_estilo_layout, obter_paleta_cores
from src.api_client import obter_estados_municipios, consultar_cnes_detalhado

# configuracao da pagina
st.set_page_config(page_title="CNES - Estabelecimentos | Painel DATASUS", layout="wide")
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
st.title("Cadastro Nacional de Estabelecimentos de Saúde (CNES)")
st.markdown(
    f"""
    <p class="text-secondary mb-4" style="font-size: 14px; margin-top: -10px;">
        Infraestrutura de Saúde — <b>{st.session_state.mun_selecionado['nome']} ({st.session_state.uf_selecionada})</b>
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# Carrega os dados detalhados do CNES
try:
    with st.spinner("Buscando os estabelecimentos no banco de dados..."):
        df = consultar_cnes_detalhado(st.session_state.mun_selecionado['id'])
except Exception as e:
    st.error(f"Não foi possível obter os dados do CNES: {e}")
    df = pd.DataFrame()

if df.empty:
    st.warning("Nenhum estabelecimento de saúde encontrado no CNES para esta localidade.")
    st.stop()

# Garante tipos string para evitar crashes de serialização
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].fillna("").astype(str)

# Filtros do catálogo
st.sidebar.markdown("### Filtros do CNES")
tipos = sorted([t for t in df["descricao_tipo_unidade"].unique() if t])
tipos_sel = st.sidebar.multiselect("Tipo de Unidade", options=tipos, default=tipos)

bairros = sorted([b for b in df["bairro_estabelecimento"].unique() if b])
bairros_sel = st.sidebar.multiselect("Bairro", options=bairros, default=[])

esferas = sorted([e for e in df["descricao_esfera_administrativa"].unique() if e])
esferas_sel = st.sidebar.multiselect("Esfera Administrativa", options=esferas, default=[])

turnos = sorted([t for t in df["descricao_turno_atendimento"].unique() if t])
turnos_sel = st.sidebar.multiselect("Turno de Atendimento", options=turnos, default=[])

apenas_hospitalares = st.sidebar.checkbox("Somente unidades hospitalares", value=False)

# Aplica filtros
filtrado = df[df["descricao_tipo_unidade"].isin(tipos_sel)]
if bairros_sel:
    filtrado = filtrado[filtrado["bairro_estabelecimento"].isin(bairros_sel)]
if esferas_sel:
    filtrado = filtrado[filtrado["descricao_esfera_administrativa"].isin(esferas_sel)]
if turnos_sel:
    filtrado = filtrado[filtrado["descricao_turno_atendimento"].isin(turnos_sel)]
if apenas_hospitalares:
    filtrado = filtrado[filtrado["estabelecimento_possui_atendimento_hospitalar"].astype(int) == 1]

# KPIs
total = len(filtrado)
hospitais = int(filtrado["estabelecimento_possui_atendimento_hospitalar"].astype(int).sum())
c_cirurgico = int(filtrado["estabelecimento_possui_centro_cirurgico"].astype(int).sum())
atend_24h = int((filtrado["descricao_turno_atendimento"] == "ATENDIMENTO 24 HORAS").sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Estabelecimentos", f"{total:,}".replace(",", "."))
c2.metric("Unidades Hospitalares", hospitais)
c3.metric("Centros Cirúrgicos", c_cirurgico)
c4.metric("Atendimento 24h", atend_24h)

st.markdown("---")

# Gráficos
col1, col2 = st.columns(2)
with col1:
    df_tipo = filtrado.groupby("descricao_tipo_unidade").size().reset_index(name="Quantidade").sort_values("Quantidade", ascending=False)
    fig = px.bar(df_tipo, x="Quantidade", y="descricao_tipo_unidade", orientation="h", title="Estabelecimentos por Tipo de Unidade", color_discrete_sequence=[colors["internacoes"]])
    aplicar_estilo_layout(fig, "Distribuição por Tipo de Unidade", x_title="Quantidade", y_title="")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_esf = filtrado.groupby("descricao_esfera_administrativa").size().reset_index(name="Quantidade").sort_values("Quantidade", ascending=False)
    fig2 = px.pie(df_esf, names="descricao_esfera_administrativa", values="Quantidade", hole=0.45, title="Esfera Administrativa", color_discrete_sequence=colors["categorical"])
    aplicar_estilo_layout(fig2, "Distribuição por Esfera Administrativa")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Mapa
if "latitude_estabelecimento_decimo_grau" in filtrado.columns:
    map_data = filtrado.copy()
    map_data["lat"] = pd.to_numeric(map_data["latitude_estabelecimento_decimo_grau"], errors="coerce")
    map_data["lon"] = pd.to_numeric(map_data["longitude_estabelecimento_decimo_grau"], errors="coerce")
    map_data = map_data.dropna(subset=["lat", "lon"])

    if not map_data.empty:
        st.subheader("Mapa dos Estabelecimentos")
        fig_map = px.scatter_mapbox(
            map_data,
            lat="lat", lon="lon",
            hover_name="nome_fantasia",
            hover_data={"codigo_cnes": True, "descricao_tipo_unidade": True, "bairro_estabelecimento": True, "lat": False, "lon": False},
            color="descricao_tipo_unidade",
            color_discrete_sequence=colors["categorical"],
            zoom=10,
            height=500
        )
        fig_map.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("---")

# Tabela do catálogo
st.subheader("Catálogo de Estabelecimentos")
cols_exib = ["codigo_cnes", "nome_fantasia", "descricao_tipo_unidade", "descricao_esfera_administrativa", "descricao_turno_atendimento", "bairro_estabelecimento"]
colunas_presentes = [c for c in cols_exib if c in filtrado.columns]
catalogo = filtrado[colunas_presentes].copy()
catalogo.columns = ["CNES", "Nome Fantasia", "Tipo de Unidade", "Esfera Administrativa", "Turno de Atendimento", "Bairro"]
for col in catalogo.columns:
    catalogo[col] = catalogo[col].fillna("").astype(str)

st.dataframe(catalogo, use_container_width=True, hide_index=True)
st.caption(f"Total de {len(catalogo)} estabelecimentos listados.")
