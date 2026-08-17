import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# coloca a pasta raiz no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.charts import injetar_custom_css, aplicar_estilo_layout, obter_paleta_cores
from src.api_client import obter_estados_municipios, consultar_sisagua, consultar_sisvan

# configuracao da pagina
st.set_page_config(page_title="Saneamento & Nutrição | Painel DATASUS", layout="wide")
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
    
    mun_name_sel = st.selectbox("Município", options=mun_nomes, index=mun_index)
    mun_obj_sel = next((m for m in muns_uf if m["nome"] == mun_name_sel), muns_uf[0])
    st.session_state.mun_selecionado = mun_obj_sel
    
    st.markdown("---")
    st.markdown(f"**Código IBGE:** {mun_obj_sel['id']}")
    st.markdown("---")

# Título
st.title("Saneamento, Meio Ambiente e Nutrição")
st.markdown(
    f"""
    <p class="text-secondary mb-4" style="font-size: 14px; margin-top: -10px;">
        Vigilância de Qualidade da Água (SISAGUA) e Estado Nutricional (SISVAN) — <b>{st.session_state.mun_selecionado['nome']} ({st.session_state.uf_selecionada})</b>
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# Abas
tab_agua, tab_nutri = st.tabs(["Qualidade da Água (SISAGUA)", "Vigilância Nutricional (SISVAN)"])

# 1. Qualidade da Água (SISAGUA)
with tab_agua:
    df_agua = pd.DataFrame()
    try:
        with st.spinner("Estamos buscando os dados..."):
            df_agua = consultar_sisagua(st.session_state.mun_selecionado['id'])
    except Exception as e:
        st.error(f"Não foi possível obter dados do SISAGUA da API: {e}")
        st.warning("O servidor do Ministério da Saúde pode estar lento ou indisponível para o SISAGUA no momento.")
        
    if not df_agua.empty:
        st.subheader("Vigilância da Qualidade da Água para Consumo Humano")
        st.markdown(
            """
            Registros de análises laboratoriais de amostras de água coletadas pela vigilância local, 
            identificando parâmetros físico-químicos e microbiológicos (pH, turbidez, coliformes, cloro).
            """
        )
        
        total_amostras = len(df_agua)
        param_distintos = df_agua["parametro"].nunique() if "parametro" in df_agua.columns else 0
        rotina = len(df_agua[df_agua["motivo_da_coleta"].astype(str).str.lower() == "rotina"]) if "motivo_da_coleta" in df_agua.columns else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Amostras Coletadas", total_amostras)
        c2.metric("Parâmetros Monitorados", param_distintos)
        c3.metric("Amostras de Rotina", rotina)
        
        st.markdown("---")
        
        col_chart, col_tbl = st.columns([1, 1])
        with col_chart:
            if "parametro" in df_agua.columns:
                df_param = df_agua.groupby("parametro").size().reset_index(name="Amostras")
                fig_agua = px.pie(df_param, names="parametro", values="Amostras", hole=0.45, title="Distribuição por Parâmetro Físico-Químico", color_discrete_sequence=colors["categorical"])
                aplicar_estilo_layout(fig_agua, "Tipos de Testes Realizados")
                st.plotly_chart(fig_agua, use_container_width=True)
            else:
                st.info("Coluna de parâmetro indisponível no retorno da API.")
                
        with col_tbl:
            st.markdown("#### Últimas Coletas Registradas")
            cols_exib = [c for c in ["data_da_coleta", "nome_da_forma_de_abastecimento", "parametro", "resultado"] if c in df_agua.columns]
            df_exib = df_agua[cols_exib].copy()
            df_exib.columns = [c.replace("_", " ").title() for c in cols_exib]
            for col in df_exib.columns:
                df_exib[col] = df_exib[col].fillna("").astype(str)
            st.dataframe(df_exib, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum registro do SISAGUA encontrado na API pública para esta localidade.")

# 2. Vigilância Nutricional (SISVAN)
    df_nutri = pd.DataFrame()
    try:
        with st.spinner("Estamos buscando os dados..."):
            df_nutri = consultar_sisvan(st.session_state.mun_selecionado['id'])
    except Exception as e:
        st.error(f"Não foi possível obter dados do SISVAN da API: {e}")
        
    if not df_nutri.empty:
        st.subheader("Vigilância Alimentar e Nutricional")
        st.markdown(
            """
            Acompanhamento de peso, altura, IMC e classificação do estado nutricional de cidadãos 
            atendidos na Atenção Básica (incluindo beneficiários do Bolsa Família / Auxílio Brasil).
            """
        )
        
        total_nutri = len(df_nutri)
        fases_vida = df_nutri["fase_vida"].nunique() if "fase_vida" in df_nutri.columns else 0
        sist_origem = df_nutri["sistema_origem_acompanhamento"].nunique() if "sistema_origem_acompanhamento" in df_nutri.columns else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Acompanhamentos Registrados", total_nutri)
        c2.metric("Fases da Vida Monitoradas", fases_vida)
        c3.metric("Origens de Dados", sist_origem)
        
        st.markdown("---")
        
        col_chart, col_tbl = st.columns([1, 1])
        with col_chart:
            if "peso_x_idade" in df_nutri.columns:
                df_estado = df_nutri.groupby("peso_x_idade").size().reset_index(name="Quantidade")
                fig_nutri = px.pie(df_estado, names="peso_x_idade", values="Quantidade", hole=0.45, title="Avaliação do Peso por Idade", color_discrete_sequence=colors["categorical"])
                aplicar_estilo_layout(fig_nutri, "Estado Nutricional (Peso x Idade)")
                st.plotly_chart(fig_nutri, use_container_width=True)
            else:
                st.info("Status nutricional indisponível no retorno da API.")
                
        with col_tbl:
            st.markdown("#### Detalhamento de Faixa Etária e Peso")
            cols_exib = [c for c in ["fase_vida", "sexo", "peso", "altura", "peso_x_idade"] if c in df_nutri.columns]
            df_exib = df_nutri[cols_exib].copy()
            df_exib.columns = [c.replace("_", " ").title() for c in cols_exib]
            for col in df_exib.columns:
                df_exib[col] = df_exib[col].fillna("").astype(str)
            st.dataframe(df_exib, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum registro do SISVAN encontrado na API pública para esta localidade.")
