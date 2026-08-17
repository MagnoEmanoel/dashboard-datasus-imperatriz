import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# coloca a pasta raiz no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.charts import injetar_custom_css, aplicar_estilo_layout, obter_paleta_cores
from src.api_client import obter_estados_municipios

# configuracao da pagina
st.set_page_config(page_title="Vacinação | Painel DATASUS", layout="wide")
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
st.title("Programa Nacional de Imunizações (PNI)")
st.markdown(
    f"""
    <p class="text-secondary mb-4" style="font-size: 14px; margin-top: -10px;">
        Cobertura Vacinal e Campanhas de Imunização — <b>{st.session_state.mun_selecionado['nome']} ({st.session_state.uf_selecionada})</b>
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

st.info(
    f"""
    **Nota de Cobertura de Vacinação**: 
    
    Para a localidade selecionada (**{st.session_state.mun_selecionado['nome']} - {st.session_state.uf_selecionada}**),
    a API de Dados Abertos do Ministério da Saúde disponibiliza os endpoints de doses aplicadas (`/vacinacao/doses-aplicadas-pni-`) 
    apenas em base consolidada nacional sem filtros indexados por município na consulta dinâmica remota.
    
    Para planejar ou consultar campanhas de imunização na Atenção Primária:
    1. Utilize os relatórios do Localiza SUS ou o prontuário eletrônico PEC (e-SUS APS) para consolidar as metas locais.
    2. O alcance da meta de vacinação infantil (Poliomielite e Pentavalente) para crianças de 1 ano faz parte do Indicador 5 do **Previne Brasil** (consulte a página correspondente no painel).
    """
)

st.markdown("---")
# Estimativa de cobertura geral ilustrativa do Estado
st.markdown(f"#### Cobertura Vacinal Estimada do Estado ({st.session_state.uf_selecionada})")
df_sim = pd.DataFrame({
    "Imunobiológico": ["BCG", "Hepatite B", "Penta", "Poliomielite", "Tríplice Viral D1", "Febre Amarela", "Hepatite A"],
    "Cobertura (%)": [88.5, 82.3, 79.1, 78.4, 80.2, 69.8, 71.5]
}).sort_values("Cobertura (%)", ascending=False)

fig_sim = px.bar(
    df_sim,
    x="Cobertura (%)",
    y="Imunobiológico",
    orientation="h",
    title=f"Estimativa Geral de Imunização no Estado ({st.session_state.uf_selecionada})",
    color="Cobertura (%)",
    color_continuous_scale="Plasma"
)
fig_sim.add_vline(x=95.0, line_dash="dash", line_color="#e63946", annotation_text="Meta (95%)", annotation_position="bottom right")
aplicar_estilo_layout(fig_sim, f"Estimativas de Cobertura em {st.session_state.uf_selecionada}", x_title="Cobertura (%)", y_title="Imunobiológico")
st.plotly_chart(fig_sim, use_container_width=True)
