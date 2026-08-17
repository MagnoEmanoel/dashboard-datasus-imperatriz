import streamlit as st
import pandas as pd
import sys
import os

# configuracao da pagina do Streamlit (DEVE ser o primeiro comando)
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
        # Padrão para Imperatriz se UF for MA, senão o primeiro da lista
        imperatriz_idx = next((i for i, m in enumerate(muns_uf) if m["id"] == "210530"), 0)
        mun_index = imperatriz_idx if uf_sel == "MA" else 0
        
    mun_nome_sel = st.selectbox("Município", options=mun_nomes, index=mun_index)
    mun_obj_sel = next((m for m in muns_uf if m["nome"] == mun_nome_sel), muns_uf[0])
    
    # Salva no session state
    st.session_state.mun_selecionado = mun_obj_sel
    
    st.markdown("---")
    st.markdown(f"**Código IBGE:** {mun_obj_sel['id']}")
    st.markdown("---")

# Título Principal
st.title("Painel de Gestão e Saúde Pública - SUS")
st.markdown(
    f"""
    <p class="text-secondary mb-4" style="font-size: 14px; margin-top: -10px;">
        Vigilância Epidemiológica, Atenção Primária e Infraestrutura de Saúde — <b>{st.session_state.mun_selecionado['nome']} ({st.session_state.uf_selecionada})</b>
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# Consulta os estabelecimentos do CNES
try:
    with st.spinner("Estamos buscando os dados..."):
        df_cnes = consultar_cnes_estabelecimentos(st.session_state.mun_selecionado['id'])
except Exception as e:
    st.error(f"Não foi possível obter os dados do CNES do Ministério da Saúde: {e}")
    st.warning("O servidor do DATASUS pode estar instável ou lento no momento. Tente recarregar a página.")
    df_cnes = pd.DataFrame()

if not df_cnes.empty:
    # Calcula KPIs
    total_estab = len(df_cnes)
    
    # Garante tipo numérico para soma correta e livre de erros de NoneType/NaN
    def obter_soma_campo(col_name):
        col = df_cnes.get(col_name)
        if col is None:
            return 0
        return int(pd.to_numeric(col, errors="coerce").fillna(0).sum())

    cirurgicos = obter_soma_campo('estabelecimento_possui_centro_cirurgico')
    obstetricos = obter_soma_campo('estabelecimento_possui_centro_obstetrico')
    neonatais = obter_soma_campo('estabelecimento_possui_centro_neonatal')
    hospitalares = obter_soma_campo('estabelecimento_possui_atendimento_hospitalar')

    
    st.markdown(
        f"""
<div class="row g-4 mb-5">
<!-- Card 1: Total Estabelecimentos -->
<div class="col-12 col-md-6 col-lg-3">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['internacoes']} !important; border-radius: 8px; background-color: #ffffff;">
<span class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em; margin-bottom: 8px; display: block;">Total Estabelecimentos (CNES)</span>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{total_estab}</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">Registros ativos no cadastro local</div>
</div>
</div>

<!-- Card 2: Leitos / Unidades Hospitalares -->
<div class="col-12 col-md-6 col-lg-3">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['mortalidade_infantil']} !important; border-radius: 8px; background-color: #ffffff;">
<span class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em; margin-bottom: 8px; display: block;">Unidades Hospitalares</span>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{int(hospitalares)}</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">Possuem atendimento de internação</div>
</div>
</div>

<!-- Card 3: Centro Cirúrgico -->
<div class="col-12 col-md-6 col-lg-3">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['nascimentos_emerald']} !important; border-radius: 8px; background-color: #ffffff;">
<span class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em; margin-bottom: 8px; display: block;">Centros Cirúrgicos</span>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{int(cirurgicos)}</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">Estruturas de média/alta complexidade</div>
</div>
</div>

<!-- Card 4: Centro Obstétrico -->
<div class="col-12 col-md-6 col-lg-3">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['nascimentos_amber']} !important; border-radius: 8px; background-color: #ffffff;">
<span class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em; margin-bottom: 8px; display: block;">Centros Obstétricos</span>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{int(obstetricos)}</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">Apoio a partos e urgências maternas</div>
</div>
</div>
</div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    st.subheader("Cadastro Nacional de Estabelecimentos de Saúde (CNES)")
    cnes_exib = df_cnes[["codigo_cnes", "nome_fantasia", "descricao_esfera_administrativa", "descricao_turno_atendimento", "bairro_estabelecimento"]].copy()
    cnes_exib.columns = ["CNES", "Nome Fantasia", "Esfera Administrativa", "Turno de Atendimento", "Bairro"]
    
    # Garante tipo string e sem NaNs para evitar crash de segmentação no serializador PyArrow
    for col in cnes_exib.columns:
        cnes_exib[col] = cnes_exib[col].fillna("").astype(str)
        
    st.dataframe(cnes_exib.head(100), use_container_width=True, hide_index=True)
else:
    st.warning("Nenhum estabelecimento de saúde encontrado no CNES para esta localidade.")

# secao informativa sobre o painel
st.markdown(
    f"""
<div class="row g-4 mt-2">
<!-- Coluna Esquerda: Sobre o Painel -->
<div class="col-12">
<div class="card p-4 border-light shadow-sm" style="background-color: #ffffff; border-radius: 8px;">
<div class="border-bottom border-light pb-3 mb-3">
<h5 class="text-dark font-sans fw-bold mb-0">Sobre este Painel Integrado por Categorias</h5>
</div>
<p class="text-secondary leading-relaxed font-sans mb-4" style="font-size: 13px;">
Acompanhe os principais indicadores públicos do SUS a partir das categorias oficiais de dados abertos do Ministério da Saúde. Selecione o Estado e Município desejados no menu lateral para atualizar os relatórios de todas as páginas em tempo real. As categorias estão estruturadas da seguinte forma:
</p>

<div class="row g-3">
<div class="col-12 col-md-6 col-lg-3">
<div class="p-3 bg-light border border-light rounded h-100" style="border-radius: 6px;">
<div class="text-xs fw-bold text-dark font-sans mb-1" style="font-size: 12px;">Vigilância e Meio Ambiente</div>
<p class="text-secondary mb-0 font-sans" style="font-size: 11px; line-height: 1.5;">
Análise de agravos compulsórios como as Arboviroses (Dengue, Zika, Chikungunya e Febre Amarela humana).
</p>
</div>
</div>
<div class="col-12 col-md-6 col-lg-3">
<div class="p-3 bg-light border border-light rounded h-100" style="border-radius: 6px;">
<div class="text-xs fw-bold text-dark font-sans mb-1" style="font-size: 12px;">Vacinação</div>
<p class="text-secondary mb-0 font-sans" style="font-size: 11px; line-height: 1.5;">
Mapeamento de imunização e dados de cobertura e doses aplicadas pelo PNI.
</p>
</div>
</div>
<div class="col-12 col-md-6 col-lg-3">
<div class="p-3 bg-light border border-light rounded h-100" style="border-radius: 6px;">
<div class="text-xs fw-bold text-dark font-sans mb-1" style="font-size: 12px;">Atenção Primária e Assistência</div>
<p class="text-secondary mb-0 font-sans" style="font-size: 11px; line-height: 1.5;">
Monitoramento de equipes, Mais Médicos (PMMB) e os indicadores do Programa Previne Brasil.
</p>
</div>
</div>
<div class="col-12 col-md-6 col-lg-3">
<div class="p-3 bg-light border border-light rounded h-100" style="border-radius: 6px;">
<div class="text-xs fw-bold text-dark font-sans mb-1" style="font-size: 12px;">Saneamento e Nutrição</div>
<p class="text-secondary mb-0 font-sans" style="font-size: 11px; line-height: 1.5;">
Vigilância da qualidade da água para consumo (SISAGUA) e acompanhamento nutricional da população (SISVAN).
</p>
</div>
</div>
</div>
</div>
</div>
</div>

<!-- Footer -->
<p class="text-center text-secondary mt-5 border-top border-light pt-4 font-sans" style="font-size: 10px; max-w: 700px; margin: 30px auto 0;">
Origem dos dados: API de Dados Abertos do Ministério da Saúde. Mapeamento nacional atualizado em tempo real.
</p>
""",
    unsafe_allow_html=True
)
