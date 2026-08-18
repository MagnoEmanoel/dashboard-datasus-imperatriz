import streamlit as st
import pandas as pd
import sys
import os

# Configuracao da pagina do Streamlit (DEVE ser o primeiro comando)
st.set_page_config(
    page_title="Painel DATASUS - Gestão do SUS",
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.charts import injetar_custom_css, obter_paleta_cores
from src.api_client import obter_estados_municipios, consultar_cnes_estabelecimentos

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
    
    # Estado (UF) selectbox
    uf_index = ufs.index(st.session_state.uf_selecionada) if st.session_state.uf_selecionada in ufs else ufs.index('MA')
    uf_sel = st.selectbox("Estado (UF)", options=ufs, index=uf_index)
    st.session_state.uf_selecionada = uf_sel
    
    # Municípios correspondentes à UF
    muns_uf = mun_map.get(uf_sel, [{"id": "210530", "nome": "Imperatriz"}])
    mun_nomes = [m["nome"] for m in muns_uf]
    
    # Encontra o índice correspondente no selectbox
    current_mun_nome = st.session_state.mun_selecionado.get('nome', '')
    if current_mun_nome in mun_nomes:
        mun_index = mun_nomes.index(current_mun_nome)
    else:
        imperatriz_idx = next((i for i, m in enumerate(muns_uf) if m["id"] == "210530"), 0)
        mun_index = imperatriz_idx if uf_sel == "MA" else 0
        
    mun_nome_sel = st.selectbox("Município", options=mun_nomes, index=mun_index)
    mun_obj_sel = next((m for m in muns_uf if m["nome"] == mun_nome_sel), muns_uf[0])
    
    # Salva no session state
    st.session_state.mun_selecionado = mun_obj_sel
    
    st.markdown("---")
    st.markdown(f"**Código IBGE:** {mun_obj_sel['id']}")
    st.markdown("---")

# Cabeçalho Institucional Limpo e Profissional
st.markdown(
    f"""
    <div style="padding-bottom: 16px; margin-bottom: 24px; border-bottom: 1px solid #e2e8f0;">
        <h1 style="font-size: 26px; font-weight: 700; color: #0f172a; margin: 0 0 6px 0; letter-spacing: -0.02em;">
            Painel de Gestão e Saúde Pública - SUS
        </h1>
        <p style="font-size: 14px; color: #64748b; margin: 0; line-height: 1.5;">
            Vigilância Epidemiológica, Atenção Primária, Infraestrutura de Saúde e Saneamento — 
            <strong style="color: #0f172a;">{st.session_state.mun_selecionado['nome']} ({st.session_state.uf_selecionada})</strong>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Consulta os estabelecimentos do CNES
try:
    with st.spinner("Buscando indicadores do CNES..."):
        df_cnes = consultar_cnes_estabelecimentos(st.session_state.mun_selecionado['id'])
except Exception as e:
    st.error(f"Não foi possível obter os dados do CNES do Ministério da Saúde: {e}")
    st.warning("O servidor do DATASUS pode estar instável ou lento no momento. Tente recarregar a página.")
    df_cnes = pd.DataFrame()

if not df_cnes.empty:
    total_estab = len(df_cnes)
    
    def obter_soma_campo(col_name):
        col = df_cnes.get(col_name)
        if col is None:
            return 0
        return int(pd.to_numeric(col, errors="coerce").fillna(0).sum())

    cirurgicos = obter_soma_campo('estabelecimento_possui_centro_cirurgico')
    obstetricos = obter_soma_campo('estabelecimento_possui_centro_obstetrico')
    hospitalares = obter_soma_campo('estabelecimento_possui_atendimento_hospitalar')

    # Grid de KPIs Limpos (Sem Gradientes ou Emojis)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #ff4b4b;">
                <div class="metric-title">Total Estabelecimentos (CNES)</div>
                <div class="metric-value">{total_estab}</div>
                <div class="metric-subtitle">Unidades ativas cadastradas</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #1c83e1;">
                <div class="metric-title">Unidades Hospitalares</div>
                <div class="metric-value">{int(hospitalares)}</div>
                <div class="metric-subtitle">Com atendimento de internação</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #00d4b1;">
                <div class="metric-title">Centros Cirúrgicos</div>
                <div class="metric-value">{int(cirurgicos)}</div>
                <div class="metric-subtitle">Estruturas cirúrgicas ativas</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #ffbd45;">
                <div class="metric-title">Centros Obstétricos</div>
                <div class="metric-value">{int(obstetricos)}</div>
                <div class="metric-subtitle">Apoio a partos e urgências</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabela Institucional do CNES
    st.markdown("<h3 style='font-size: 16px; font-weight: 600; color: #0f172a; margin-bottom: 12px;'>Cadastro Nacional de Estabelecimentos de Saúde (CNES)</h3>", unsafe_allow_html=True)
    cnes_exib = df_cnes[["codigo_cnes", "nome_fantasia", "descricao_esfera_administrativa", "descricao_turno_atendimento", "bairro_estabelecimento"]].copy()
    cnes_exib.columns = ["CNES", "Nome Fantasia", "Esfera Administrativa", "Turno de Atendimento", "Bairro"]
    
    for col in cnes_exib.columns:
        cnes_exib[col] = cnes_exib[col].fillna("").astype(str)
        
    st.dataframe(cnes_exib.head(100), use_container_width=True, hide_index=True)
else:
    st.warning("Nenhum estabelecimento de saúde encontrado no CNES para esta localidade.")

st.markdown("<br>", unsafe_allow_html=True)

# Seções do Painel (Sem emojis)
st.markdown("<h3 style='font-size: 16px; font-weight: 600; color: #0f172a; margin-bottom: 12px;'>Estrutura das Categorias de Dados</h3>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(
        """
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; height: 100%;">
            <div style="font-weight: 600; font-size: 13px; color: #0f172a; margin-bottom: 4px;">Vigilância e Meio Ambiente</div>
            <p style="font-size: 11px; color: #64748b; margin: 0; line-height: 1.4;">
                Análise epidemiológica de Dengue, Zika, Chikungunya e Febre Amarela.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
with m2:
    st.markdown(
        """
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; height: 100%;">
            <div style="font-weight: 600; font-size: 13px; color: #0f172a; margin-bottom: 4px;">Vacinação</div>
            <p style="font-size: 11px; color: #64748b; margin: 0; line-height: 1.4;">
                Mapeamento de imunização, cobertura vacinal e doses aplicadas.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
with m3:
    st.markdown(
        """
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; height: 100%;">
            <div style="font-weight: 600; font-size: 13px; color: #0f172a; margin-bottom: 4px;">Atenção Primária e Assistência</div>
            <p style="font-size: 11px; color: #64748b; margin: 0; line-height: 1.4;">
                Equipes de Saúde da Família, PMMB e indicadores do Previne Brasil.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
with m4:
    st.markdown(
        """
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; height: 100%;">
            <div style="font-weight: 600; font-size: 13px; color: #0f172a; margin-bottom: 4px;">Saneamento e Nutrição</div>
            <p style="font-size: 11px; color: #64748b; margin: 0; line-height: 1.4;">
                Qualidade da água para consumo (SISAGUA) e acompanhamento no SISVAN.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """
    <p style="text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 16px;">
        Origem dos dados: API de Dados Abertos do Ministério da Saúde e Base de Dados do CNES (PostgreSQL).
    </p>
    """,
    unsafe_allow_html=True
)
