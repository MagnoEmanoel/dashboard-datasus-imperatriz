import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# coloca a pasta raiz no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.charts import injetar_custom_css, aplicar_estilo_layout, obter_paleta_cores
from src.api_client import obter_estados_municipios, consultar_arbovirose, consultar_febre_amarela

# configuracao da pagina
st.set_page_config(page_title="Vigilância e Meio Ambiente | Painel DATASUS", layout="wide")
st.markdown(injetar_custom_css(), unsafe_allow_html=True)

colors = obter_paleta_cores()

# Tradutores de códigos
CLASSI_MAP_DENGUE = {"10": "Dengue", "11": "Dengue Alarme", "12": "Dengue Grave", "5": "Ignorado"}
CLASSI_MAP_ZIKA = {"11": "Zika Confirmado", "12": "Zika Grave", "5": "Ignorado"}
CLASSI_MAP_CHIK = {"13": "Chikungunya Confirmado", "10": "Co-infecção Dengue", "5": "Ignorado"}
EVOLUCAO_MAP = {"1": "Cura", "2": "Óbito da Doença", "3": "Óbito outras causas", "4": "Em Investigação", "9": "Ignorado"}
HOSPITALIZ_MAP = {"1": "Sim", "2": "Não", "9": "Ignorado"}
GESTANTE_MAP = {"1": "1º Trimestre", "2": "2º Trimestre", "3": "3º Trimestre", "4": "Ignorado", "5": "Não Gestante", "6": "Não se aplica"}

def decode_sinan_age(age_val):
    if pd.isna(age_val) or age_val is None:
        return None
    try:
        val = int(float(age_val))
        prefix = val // 1000
        age = val % 1000
        if prefix == 4:
            return age
        elif prefix in [1, 2, 3]:
            return 0
        return val if val < 120 else None
    except Exception:
        return None

def categorizar_faixa_etaria(idade):
    if idade is None or pd.isna(idade):
        return "Ignorado"
    if idade < 1:
        return "Menor de 1 ano"
    elif idade <= 4:
        return "1 a 4 anos"
    elif idade <= 14:
        return "5 a 14 anos"
    elif idade <= 24:
        return "15 a 24 anos"
    elif idade <= 34:
        return "25 a 34 anos"
    elif idade <= 44:
        return "35 a 44 anos"
    elif idade <= 54:
        return "45 a 54 anos"
    elif idade <= 64:
        return "55 a 64 anos"
    elif idade <= 74:
        return "65 a 74 anos"
    else:
        return "75 anos ou mais"

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
    
    # Filtro de Ano específico da Vigilância
    ano_sel = st.selectbox("Ano de Referência", options=[str(y) for y in range(2026, 2017, -1)], index=2) # default 2024

# Título
st.title("Vigilância Epidemiológica e Meio Ambiente")
st.markdown(
    f"""
    <p class="text-secondary mb-4" style="font-size: 14px; margin-top: -10px;">
        Monitoramento de Arboviroses e Agravos — <b>{st.session_state.mun_selecionado['nome']} ({st.session_state.uf_selecionada})</b> para o ano <b>{ano_sel}</b>
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# Faz as consultas à API de forma independente
df_dengue = pd.DataFrame()
df_chiky = pd.DataFrame()
df_zika = pd.DataFrame()
df_fa = pd.DataFrame()

with st.spinner("Estamos buscando os dados..."):
    # Dengue
    try:
        df_dengue = consultar_arbovirose("arboviroses/dengue", "dengue", st.session_state.mun_selecionado['id'], ano_sel)
    except Exception as e:
        st.error(f"Não foi possível obter dados de Dengue da API: {e}")
        st.warning("O servidor do Ministério da Saúde pode estar indisponível ou instável para Dengue no momento.")

    # Chikungunya
    try:
        df_chiky = consultar_arbovirose("arboviroses/chikungunya", "chikungunya", st.session_state.mun_selecionado['id'], ano_sel)
    except Exception as e:
        st.error(f"Não foi possível obter dados de Chikungunya da API: {e}")
        
    # Zika
    try:
        df_zika = consultar_arbovirose("arboviroses/zikavirus", "zikavirus", st.session_state.mun_selecionado['id'], ano_sel)
    except Exception as e:
        st.error(f"Não foi possível obter dados de Zika da API: {e}")
        
    # Febre Amarela
    try:
        df_fa = consultar_febre_amarela(st.session_state.mun_selecionado['id'])
    except Exception as e:
        st.error(f"Não foi possível obter dados de Febre Amarela da API: {e}")
        st.warning("A base nacional de Febre Amarela pode ser lenta para carregar na primeira consulta.")

# Abas por agravo
tab_dengue, tab_chiky, tab_zika, tab_fa = st.tabs(["Dengue", "Chikungunya", "Zika Vírus", "Febre Amarela (Humana)"])

# 1. Dengue
with tab_dengue:
    if not df_dengue.empty:
        total_dengue = len(df_dengue)
        df_dengue["classi_fin"] = df_dengue["classi_fin"].astype(str).str.split(".").str[0]
        df_dengue["evolucao"] = df_dengue["evolucao"].astype(str).str.split(".").str[0]
        df_dengue["hospitaliz"] = df_dengue["hospitaliz"].astype(str).str.split(".").str[0]
        df_dengue["idade_anos"] = df_dengue["nu_idade_n"].apply(decode_sinan_age)
        df_dengue["faixa_etaria"] = df_dengue["idade_anos"].apply(categorizar_faixa_etaria)
        
        hosp = len(df_dengue[df_dengue["hospitaliz"] == "1"])
        obitos = len(df_dengue[df_dengue["evolucao"] == "2"])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Casos Notificados", total_dengue)
        c2.metric("Internações", hosp)
        c3.metric("Óbitos Confirmados", obitos)
        
        st.markdown("---")
        col_donut, col_age = st.columns(2)
        with col_donut:
            df_sex = df_dengue.groupby("cs_sexo").size().reset_index(name="Casos")
            df_sex["sexo_nome"] = df_sex["cs_sexo"].map({"M": "Masculino", "F": "Feminino"}).fillna("Ignorado")
            fig = px.pie(df_sex, names="sexo_nome", values="Casos", hole=0.45, title="Casos por Sexo", color_discrete_sequence=colors["categorical"])
            aplicar_estilo_layout(fig, "Perfil por Sexo")
            st.plotly_chart(fig, use_container_width=True)
            
        with col_age:
            df_age = df_dengue.groupby("faixa_etaria").size().reset_index(name="Casos")
            fig = px.bar(df_age, x="faixa_etaria", y="Casos", title="Casos por Faixa Etária", color_discrete_sequence=[colors["mortalidade_infantil"]])
            aplicar_estilo_layout(fig, "Perfil por Idade", x_title="Faixa Etária", y_title="Casos")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum registro de Dengue encontrado para esta localidade no ano selecionado.")

# 2. Chikungunya
with tab_chiky:
    if not df_chiky.empty:
        total_chiky = len(df_chiky)
        df_chiky["classi_fin"] = df_chiky["classi_fin"].astype(str).str.split(".").str[0]
        df_chiky["evolucao"] = df_chiky["evolucao"].astype(str).str.split(".").str[0]
        df_chiky["hospitaliz"] = df_chiky["hospitaliz"].astype(str).str.split(".").str[0]
        df_chiky["idade_anos"] = df_chiky["nu_idade_n"].apply(decode_sinan_age)
        df_chiky["faixa_etaria"] = df_chiky["idade_anos"].apply(categorizar_faixa_etaria)
        
        hosp = len(df_chiky[df_chiky["hospitaliz"] == "1"])
        obitos = len(df_chiky[df_chiky["evolucao"] == "2"])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Casos Notificados", total_chiky)
        c2.metric("Internações", hosp)
        c3.metric("Óbitos Confirmados", obitos)
        
        st.markdown("---")
        col_donut, col_age = st.columns(2)
        with col_donut:
            df_sex = df_chiky.groupby("cs_sexo").size().reset_index(name="Casos")
            df_sex["sexo_nome"] = df_sex["cs_sexo"].map({"M": "Masculino", "F": "Feminino"}).fillna("Ignorado")
            fig = px.pie(df_sex, names="sexo_nome", values="Casos", hole=0.45, title="Casos por Sexo", color_discrete_sequence=colors["categorical"])
            aplicar_estilo_layout(fig, "Perfil por Sexo")
            st.plotly_chart(fig, use_container_width=True)
            
        with col_age:
            df_age = df_chiky.groupby("faixa_etaria").size().reset_index(name="Casos")
            fig = px.bar(df_age, x="faixa_etaria", y="Casos", title="Casos por Faixa Etária", color_discrete_sequence=[colors["internacoes"]])
            aplicar_estilo_layout(fig, "Perfil por Idade", x_title="Faixa Etária", y_title="Casos")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum registro de Chikungunya encontrado para esta localidade no ano selecionado.")

# 3. Zika
with tab_zika:
    if not df_zika.empty:
        total_zika = len(df_zika)
        df_zika["classi_fin"] = df_zika["classi_fin"].astype(str).str.split(".").str[0]
        df_zika["evolucao"] = df_zika["evolucao"].astype(str).str.split(".").str[0]
        df_zika["cs_gestant"] = df_zika["cs_gestant"].astype(str).str.split(".").str[0]
        df_zika["idade_anos"] = df_zika["nu_idade_n"].apply(decode_sinan_age)
        df_zika["faixa_etaria"] = df_zika["idade_anos"].apply(categorizar_faixa_etaria)
        
        gestantes = len(df_zika[df_zika["cs_gestant"].isin(["1", "2", "3", "4"])])
        obitos = len(df_zika[df_zika["evolucao"] == "2"])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Casos Notificados", total_zika)
        c2.metric("Gestantes Notificadas", gestantes)
        c3.metric("Óbitos Confirmados", obitos)
        
        st.markdown("---")
        col_donut, col_age = st.columns(2)
        with col_donut:
            df_gest = df_zika.groupby("cs_gestant").size().reset_index(name="Casos")
            df_gest["Estado Gestacional"] = df_gest["cs_gestant"].map(GESTANTE_MAP).fillna("Ignorado")
            fig = px.bar(df_gest, x="Casos", y="Estado Gestacional", orientation="h", title="Zika por Status Gestacional", color_discrete_sequence=[colors["nascimentos_emerald"]])
            aplicar_estilo_layout(fig, "Zika em Gestantes")
            st.plotly_chart(fig, use_container_width=True)
            
        with col_age:
            df_age = df_zika.groupby("faixa_etaria").size().reset_index(name="Casos")
            fig = px.bar(df_age, x="faixa_etaria", y="Casos", title="Casos por Faixa Etária", color_discrete_sequence=[colors["nascimentos_emerald"]])
            aplicar_estilo_layout(fig, "Perfil por Idade", x_title="Faixa Etária", y_title="Casos")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum registro de Zika Vírus encontrado para esta localidade no ano selecionado.")

# 4. Febre Amarela
with tab_fa:
    # Filtra febre amarela para o ano selecionado
    if not df_fa.empty:
        df_fa_ano = df_fa[df_fa["ano_is"].astype(str) == ano_sel].copy()
    else:
        df_fa_ano = pd.DataFrame()
        
    if not df_fa_ano.empty:
        total_fa = len(df_fa_ano)
        df_fa_ano["obito"] = df_fa_ano["obito"].astype(str).str.upper().str.strip()
        obitos_fa = len(df_fa_ano[df_fa_ano["obito"] == "SIM"])
        
        c1, c2 = st.columns(2)
        c1.metric("Casos Humanos", total_fa)
        c2.metric("Óbitos Humanos", obitos_fa)
        
        st.markdown("---")
        col_donut, col_age = st.columns(2)
        with col_donut:
            df_sex = df_fa_ano.groupby("sexo").size().reset_index(name="Casos")
            df_sex["sexo_nome"] = df_sex["sexo"].map({"M": "Masculino", "F": "Feminino"}).fillna("Não Informado")
            fig = px.pie(df_sex, names="sexo_nome", values="Casos", hole=0.45, title="Casos por Sexo", color_discrete_sequence=colors["categorical"])
            aplicar_estilo_layout(fig, "Perfil por Sexo")
            st.plotly_chart(fig, use_container_width=True)
            
        with col_age:
            df_age = df_fa_ano.groupby("faixa_etaria").size().reset_index(name="Casos")
            fig = px.bar(df_age, x="faixa_etaria", y="Casos", title="Casos por Faixa Etária", color_discrete_sequence=[colors["vacinacao"]])
            aplicar_estilo_layout(fig, "Perfil por Idade", x_title="Faixa Etária", y_title="Casos")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum registro humano de Febre Amarela encontrado para esta localidade no ano selecionado.")
