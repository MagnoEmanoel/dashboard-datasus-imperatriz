import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# coloca a pasta raiz no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.charts import injetar_custom_css, aplicar_estilo_layout, obter_paleta_cores
from src.api_client import obter_estados_municipios, consultar_previne_brasil

# configuracao da pagina
st.set_page_config(page_title="Atenção Primária | Painel DATASUS", layout="wide")
st.markdown(injetar_custom_css(), unsafe_allow_html=True)

colors = obter_paleta_cores()

INDICADORES_MAP = {
    1: "Ind 1: Pré-Natal (Mínimo 6 Consultas)",
    2: "Ind 2: Pré-Natal (Exames Sífilis e HIV)",
    3: "Ind 3: Pré-Natal (Saúde Bucal)",
    4: "Ind 4: Cobertura de Exame Citopatológico",
    5: "Ind 5: Vacinação Polio e Pentavalente",
    6: "Ind 6: Hipertensos com PA Aferida",
    7: "Ind 7: Diabéticos com Hemoglobina Glicada",
    10: "Ind 1: Pré-Natal (Mínimo 6 Consultas)",
    20: "Ind 2: Pré-Natal (Exames Sífilis e HIV)",
    30: "Ind 3: Pré-Natal (Saúde Bucal)",
    40: "Ind 4: Cobertura de Exame Citopatológico",
    50: "Ind 5: Vacinação Polio e Pentavalente",
    60: "Ind 6: Hipertensos com PA Aferida",
    70: "Ind 7: Diabéticos com Hemoglobina Glicada"
}

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
st.title("Atenção Primária à Saúde (Previne Brasil)")
st.markdown(
    f"""
    <p class="text-secondary mb-4" style="font-size: 14px; margin-top: -10px;">
        Indicadores de Financiamento e Desempenho Clínico — <b>{st.session_state.mun_selecionado['nome']} ({st.session_state.uf_selecionada})</b>
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# Consulta dados Previne Brasil
df_previne = pd.DataFrame()
try:
    with st.spinner("Estamos buscando os dados..."):
        df_previne = consultar_previne_brasil(st.session_state.mun_selecionado['id'])
except Exception as e:
    st.error(f"Não foi possível obter dados do Previne Brasil da API: {e}")
    st.warning("O servidor do Ministério da Saúde pode estar lento ou indisponível para o Previne Brasil no momento.")

if not df_previne.empty:
    st.subheader("Desempenho dos Indicadores de Saúde")
    st.markdown(
        """
        O modelo de cofinanciamento federal do Programa Previne Brasil avalia 7 indicadores de desempenho cruciais 
        relacionados à saúde da mulher, saúde bucal, imunização infantil e doenças crônicas (hipertensão e diabetes).
        """
    )
    
    # Filtra quadrimestre mais recente
    quad_recente = df_previne["quadrimestre"].max()
    df_quad = df_previne[df_previne["quadrimestre"] == quad_recente].copy()
    
    df_quad["Indicador"] = df_quad["codigo_tipo_indicador"].map(INDICADORES_MAP).fillna("Indicador Não Mapeado")
    df_quad = df_quad.sort_values("codigo_tipo_indicador")
    
    # Exibe Gráfico de Barras do Desempenho
    fig_prev = px.bar(
        df_quad,
        x="percentual",
        y="Indicador",
        orientation="h",
        title=f"Resultados Consolidados no Quadrimestre: {quad_recente}",
        color="percentual",
        color_continuous_scale="RdYlGn",
        range_color=[0, 100],
        text="percentual"
    )
    fig_prev.update_traces(texttemplate='%{text}%', textposition='outside')
    aplicar_estilo_layout(fig_prev, f"Percentual de Desempenho por Indicador ({quad_recente})", x_title="Percentual Alcançado (%)", y_title="Indicador")
    st.plotly_chart(fig_prev, use_container_width=True)
    
    st.markdown("---")
    
    # Tabela detalhada
    st.markdown("#### Detalhamento das Metas de Atenção Primária")
    df_tabela = df_quad[["Indicador", "numerador", "denominador_identificado", "denominador_estimado", "percentual"]].copy()
    df_tabela.columns = ["Indicador Clinico", "Numerador (Cadastros Atendidos)", "Denominador Identificado", "Denominador Estimado (Meta)", "Percentual (%)"]
    for col in df_tabela.columns:
        df_tabela[col] = df_tabela[col].fillna("").astype(str)
    st.dataframe(df_tabela, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum indicador do Previne Brasil registrado na API pública para esta localidade.")
    
    # Exibe tabela explicativa dos indicadores
    st.markdown("---")
    st.markdown("#### O que é avaliado no Previne Brasil?")
    df_expl = pd.DataFrame({
        "Indicador": [
            "Ind 1: Consultas Pré-Natal", 
            "Ind 2: Exames Sífilis/HIV", 
            "Ind 3: Pré-Natal Odonto", 
            "Ind 4: Exame Citopatológico", 
            "Ind 5: Vacinação Infantil", 
            "Ind 6: Hipertensão", 
            "Ind 7: Diabetes"
        ],
        "Descrição": [
            "Proporção de gestantes com pelo menos 6 consultas de pré-natal realizadas, sendo a 1ª até a 12ª semana.",
            "Proporção de gestantes com realização de exames para Sífilis e HIV.",
            "Proporção de gestantes com atendimento odontológico realizado.",
            "Proporção de mulheres com coleta de exame citopatológico na APS.",
            "Proporção de crianças de 1 ano de idade vacinadas com a Polio e Pentavalente.",
            "Proporção de pessoas com hipertensão arterial sistêmica com consulta e pressão medida.",
            "Proporção de pessoas com diabetes com consulta e hemoglobina glicada solicitada."
        ],
        "Meta Recomendada": ["45%", "60%", "60%", "40%", "95%", "50%", "50%"]
    })
    st.table(df_expl)
