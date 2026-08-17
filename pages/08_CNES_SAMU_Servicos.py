import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# coloca a pasta raiz no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.charts import injetar_custom_css, aplicar_estilo_layout, obter_paleta_cores
from src.api_client import obter_estados_municipios, consultar_cnes_samu_regulacao, consultar_cnes_servicos

# configuracao da pagina
st.set_page_config(page_title="CNES - SAMU e Serviços | Painel DATASUS", layout="wide")
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
st.title("SAMU, Regulação de Urgências e Serviços (CNES)")
st.markdown(
    f"""
    <p class="text-secondary mb-4" style="font-size: 14px; margin-top: -10px;">
        Frota do SAMU 192, centrais de regulação e serviços referenciados — <b>{st.session_state.mun_selecionado['nome']} ({st.session_state.uf_selecionada})</b>
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# Carrega os dados
try:
    with st.spinner("Buscando dados de SAMU, regulação e serviços..."):
        df_veiculos, df_centrais = consultar_cnes_samu_regulacao(st.session_state.mun_selecionado['id'])
        df_servicos = consultar_cnes_servicos(st.session_state.mun_selecionado['id'])
except Exception as e:
    st.error(f"Não foi possível obter os dados de SAMU/Serviços do CNES: {e}")
    df_veiculos, df_centrais, df_servicos = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Abas
tab_samu, tab_reg, tab_serv = st.tabs(["Frota do SAMU 192", "Centrais de Regulação", "Serviços Referenciados"])

# 1. SAMU
with tab_samu:
    if not df_veiculos.empty:
        for col in df_veiculos.columns:
            df_veiculos[col] = df_veiculos[col].fillna("").astype(str)

        ativos = int((df_veiculos["data_desativacao"] == "").sum())
        c1, c2 = st.columns(2)
        c1.metric("Veículos Cadastrados", len(df_veiculos))
        c2.metric("Veículos Ativos", ativos)

        st.markdown("---")

        # Classifica por tipo com base no nome da unidade
        df_veiculos["Tipo de Veículo"] = df_veiculos["nome_fantasia"].apply(
            lambda n: "Unidade de Suporte Avançado (USA)" if "AVANCADO" in n.upper() else
                      ("Unidade de Suporte Básico (USB)" if "BASICO" in n.upper() else
                       ("Motolância" if "MOTO" in n.upper() else "Outro tipo"))
        )

        df_tipo = df_veiculos.groupby("Tipo de Veículo").size().reset_index(name="Quantidade").sort_values("Quantidade", ascending=False)
        fig = px.pie(df_tipo, names="Tipo de Veículo", values="Quantidade", hole=0.45, title="Frota por Tipo de Veículo", color_discrete_sequence=colors["categorical"])
        aplicar_estilo_layout(fig, "Composição da Frota do SAMU")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Detalhamento da Frota")
        tabela = df_veiculos[["codigo_cnes", "nome_fantasia", "placa", "chassi", "data_ativacao", "data_desativacao"]].copy()
        tabela.columns = ["CNES", "Unidade", "Placa", "Chassi", "Ativação", "Desativação"]
        st.dataframe(tabela, use_container_width=True, hide_index=True)
        st.caption(f"Total de {len(tabela)} veículos vinculados ao SAMU.")
    else:
        st.info("Nenhum veículo do SAMU encontrado para esta localidade.")

# 2. Centrais de Regulação
with tab_reg:
    if not df_centrais.empty:
        for col in df_centrais.columns:
            df_centrais[col] = df_centrais[col].fillna("").astype(str)

        c1, c2 = st.columns(2)
        c1.metric("Centrais Cadastradas", df_centrais["codigo_cnes"].nunique())
        c2.metric("Bases/Vínculos", len(df_centrais))

        st.markdown("---")
        st.subheader("Centrais de Regulação e Bases Descentralizadas")
        tabela = df_centrais[["codigo_cnes", "nome_fantasia", "nome_central", "bairro"]].copy()
        tabela.columns = ["CNES", "Unidade", "Central/Base", "Bairro"]
        st.dataframe(tabela, use_container_width=True, hide_index=True)
        st.caption(f"Total de {len(tabela)} bases de regulação registradas.")
    else:
        st.info("Nenhuma central de regulação encontrada para esta localidade.")

# 3. Serviços Referenciados
with tab_serv:
    if not df_servicos.empty:
        for col in df_servicos.columns:
            df_servicos[col] = df_servicos[col].fillna("Não Informado").astype(str)

        c1, c2 = st.columns(2)
        c1.metric("Serviços Cadastrados", len(df_servicos))
        c2.metric("Tipos Distintos", df_servicos["descricao_servico"].nunique())

        st.markdown("---")

        df_serv = df_servicos.groupby("descricao_servico").size().reset_index(name="Quantidade").sort_values("Quantidade", ascending=False)
        fig2 = px.bar(df_serv, x="Quantidade", y="descricao_servico", orientation="h", title="Serviços por Tipo", color_discrete_sequence=[colors["internacoes"]])
        aplicar_estilo_layout(fig2, "Serviços Referenciados por Tipo", x_title="Quantidade", y_title="")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.subheader("Detalhamento dos Serviços Referenciados")
        tabela = df_servicos[["codigo_cnes", "nome_fantasia", "descricao_servico", "razao_social_prestador"]].copy()
        tabela.columns = ["CNES", "Estabelecimento", "Serviço", "Prestador"]
        st.dataframe(tabela, use_container_width=True, hide_index=True)
        st.caption(f"Total de {len(tabela)} serviços referenciados cadastrados.")
    else:
        st.info("Nenhum serviço referenciado encontrado para esta localidade.")
