import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import carregar_tabela, criar_engine
from src.charts import injetar_custom_css, aplicar_estilo_layout, obter_paleta_cores

# Configuração de página (Sem emojis)
st.set_page_config(page_title="Cobertura Vacinal | DATASUS", layout="wide")
st.markdown(injetar_custom_css(), unsafe_allow_html=True)

# Cores e conexão
colors = obter_paleta_cores()
_, db_type = criar_engine()

# Título da página
st.title("Cobertura Vacinal")
st.caption(f"Fonte: SI-PNI — Sistema de Informacoes do Programa Nacional de Imunizacao / DATASUS | Banco de dados: {db_type.upper()}")
st.markdown("---")

try:
    df_vac = carregar_tabela("vacinacao_cobertura")
except Exception as e:
    st.error("Erro ao conectar ao banco de dados ou carregar tabelas de vacinacao. Verifique se realizou a ingestao de dados.")
    st.info("Execute: python src/ingest.py no terminal.")
    st.stop()

# Textos informativos detalhados por vacina (Igual ao comportamento de VacinacaoView.tsx)
INFO_VACINAS = {
    "BCG": {
        "maior": "A vacina BCG (tuberculose) mantem historicamente otimos patamares devido a aplicacao logo ao nascer na propria maternidade.",
        "menor": "A cobertura pode sofrer quedas pontuais se houver desabastecimento nacional do imunobiologico ou atrasos de registro."
    },
    "Poliomielite": {
        "maior": "A vacina contra Poliomielite costuma apresentar picos em anos de campanhas de mobilizacao nacional contra a paralisia infantil.",
        "menor": "Quedas recentes de cobertura geram alto risco de reintroducao do poliovirus selvagem no territorio municipal."
    },
    "Tríplice Viral  D1": {
        "maior": "Triplice Viral (sarampo, caxumba, rubéola) atinge coberturas elevadas quando vinculada ao calendario de creches e escolas.",
        "menor": "A hesitacao vacinal e boatos infundados sobre vacinas impactaram negativamente a adesao a este imunizante nos ultimos anos."
    },
    "Penta": {
        "maior": "A vacina Pentavalente protege contra cinco doencas graves e mantem boa adesao por fazer parte do primeiro ano de vida.",
        "menor": "Dificuldades de acesso aos postos e falta de busca ativa prejudicam as doses subsequentes do esquema vacinal."
    },
    "Febre Amarela": {
        "maior": "A cobertura vacinal de Febre Amarela atinge niveis altos apos acoes de bloqueio em periodos de alerta epidemiologico.",
        "menor": "A percepcao de baixo risco pela populacao urbana contribui para a reducao da procura espontanea nos postos."
    }
}

DEFAULT_INFO = {
    "maior": "A cobertura desta vacina reflete o engajamento das familias e as campanhas sistematicas de imunizacao.",
    "menor": "Abaixo da meta de 95%, aumenta o risco de surtos de doencas imunopreveniveis na populacao infantil."
}

try:
    # Colunas de vacinas (excluindo a coluna 'ano')
    vacinas = [col for col in df_vac.columns if col != "ano"]
    
    # Ordena os anos para garantir exibição correta
    df_vac = df_vac.sort_values(by="ano", ascending=True)
    df_vac["ano"] = df_vac["ano"].astype(str)
    
    # Encontra os dados do último ano registrado
    ultimo_ano = df_vac["ano"].iloc[-1]
    df_ultimo_ano = df_vac[df_vac["ano"] == ultimo_ano].iloc[0]
    
    # Calcula vacinas com maior e menor cobertura no último ano
    cobertura_ultimo_ano = pd.Series({v: df_ultimo_ano[v] for v in vacinas})
    vacina_max = cobertura_ultimo_ano.idxmax()
    valor_max = cobertura_ultimo_ano.max()
    vacina_min = cobertura_ultimo_ano.idxmin()
    valor_min = cobertura_ultimo_ano.min()
    
    # Quantas vacinas estão abaixo da meta ideal (95%)
    meta_cobertura = 95.0
    vacinas_abaixo_meta = (cobertura_ultimo_ano < meta_cobertura).sum()
    
    # KPIs dinâmicos do Bootstrap
    st.markdown(
        f"""
<div class="row g-4 mb-4">
<!-- Card 1: Maior Cobertura Recente -->
<div class="col-12 col-md-4">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['vacinacao']} !important; border-radius: 8px; background-color: #ffffff;">
<div class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em; margin-bottom: 8px;">Maior Cobertura ({ultimo_ano})</div>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{valor_max:.1f}%</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">Vacina: <b>{vacina_max}</b></div>
</div>
</div>

<!-- Card 2: Menor Cobertura Recente -->
<div class="col-12 col-md-4">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['mortalidade_infantil']} !important; border-radius: 8px; background-color: #ffffff;">
<div class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em; margin-bottom: 8px;">Menor Cobertura ({ultimo_ano})</div>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{valor_min:.1f}%</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">Vacina: <b>{vacina_min}</b></div>
</div>
</div>

<!-- Card 3: Abaixo da Meta -->
<div class="col-12 col-md-4">
<div class="card p-4 border-light shadow-sm h-100" style="border-left: 4px solid {colors['nascimentos_amber']} !important; border-radius: 8px; background-color: #ffffff;">
<div class="text-uppercase text-secondary fw-bold font-sans" style="font-size: 10px; letter-spacing: 0.08em; margin-bottom: 8px;">Abaixo do Ideal (&lt;95% em {ultimo_ano})</div>
<div class="fs-2 fw-bold text-dark font-monospace" style="letter-spacing: -0.03em;">{vacinas_abaixo_meta} de {len(vacinas)}</div>
<div class="text-secondary mt-3 font-sans" style="font-size: 11px;">Imunizações prioritárias em patamares de alerta epidemiológico</div>
</div>
</div>
</div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # Controles do gráfico na barra lateral
    st.sidebar.markdown("### Selecao de Vacinas")
    modo_visualizacao = st.sidebar.radio("Modo de Grafico", ["Vacina Unica", "Comparar Multiplas Vacinas"])
    
    if modo_visualizacao == "Vacina Unica":
        vacina_selecionada = st.sidebar.selectbox("Selecione a vacina para detalhar", vacinas)
        
        # Gráfico de linha da vacina selecionada
        fig = px.line(
            df_vac,
            x="ano",
            y=vacina_selecionada,
            title=f"Evolucao da Cobertura Vacinal - {vacina_selecionada}",
            labels={"ano": "Ano", vacina_selecionada: "Cobertura (%)"},
            markers=True,
            color_discrete_sequence=[colors["vacinacao"]]
        )
        
        # Adiciona linha de meta ideal (95%)
        fig.add_hline(y=meta_cobertura, line_dash="dash", line_color=colors["mortalidade_infantil"], annotation_text="Meta Ideal (95%)", annotation_position="top left")
        aplicar_estilo_layout(fig, title=f"Cobertura Vacinal: {vacina_selecionada}", x_title="Ano", y_title="Cobertura (%)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Destaques específicos da vacina selecionada (Destaque Positivo / Ponto de Atenção)
        v_info = INFO_VACINAS.get(vacina_selecionada, DEFAULT_INFO)
        st.markdown(
            f"""
<div class="row g-3 mb-4 font-sans text-secondary" style="font-size: 12px;">
    <div class="col-12 col-md-6">
        <div class="p-3 bg-light border border-light rounded" style="border-radius: 6px;">
            <span class="fw-bold text-dark d-block mb-1">Destaque Positivo</span>
            <p class="mb-0 leading-normal">{v_info['maior']}</p>
        </div>
    </div>
    <div class="col-12 col-md-6">
        <div class="p-3 bg-light border border-light rounded" style="border-radius: 6px;">
            <span class="fw-bold text-dark d-block mb-1">Ponto de Atencao</span>
            <p class="mb-0 leading-normal">{v_info['menor']}</p>
        </div>
    </div>
</div>
            """,
            unsafe_allow_html=True
        )
        
        # Tabela dos dados específicos
        st.markdown(f"#### Dados Historicos — {vacina_selecionada}")
        
        df_exib_tab = df_vac[["ano", vacina_selecionada]].copy()
        df_exib_tab["Avaliação"] = df_exib_tab[vacina_selecionada].apply(lambda x: "Meta Atingida" if x >= 95 else "Abaixo da Meta")
        
        st.dataframe(
            df_exib_tab.rename(columns={"ano": "Ano", vacina_selecionada: "Cobertura (%)", "Avaliação": "Avaliacao de Desempenho"}), 
            use_container_width=True, 
            hide_index=True
        )
        
    else:
        # Modo de comparação múltipla
        vacinas_comparar = st.sidebar.multiselect(
            "Selecione as vacinas para comparar",
            options=vacinas,
            default=vacinas[:3] if len(vacinas) >= 3 else vacinas
        )
        
        if len(vacinas_comparar) > 0:
            df_long = df_vac.melt(
                id_vars=["ano"],
                value_vars=vacinas_comparar,
                var_name="Vacina",
                value_name="Cobertura"
            )
            
            fig_comp = px.line(
                df_long,
                x="ano",
                y="Cobertura",
                color="Vacina",
                title="Comparativo de Cobertura Vacinal",
                markers=True,
                color_discrete_sequence=colors["categorical"]
            )
            fig_comp.add_hline(y=meta_cobertura, line_dash="dash", line_color=colors["mortalidade_infantil"], annotation_text="Meta Ideal (95%)", annotation_position="top left")
            aplicar_estilo_layout(fig_comp, title="Comparacao de Cobertura Vacinal entre Imunobiologicos", x_title="Ano", y_title="Cobertura (%)")
            st.plotly_chart(fig_comp, use_container_width=True)
            
            st.markdown("#### Detalhamento das Coberturas Analisadas")
            st.dataframe(df_vac[["ano"] + vacinas_comparar], use_container_width=True, hide_index=True)
        else:
            st.warning("Selecione pelo menos uma vacina na barra lateral para ver o comparativo.")
            
    # Alerta importante ao final
    st.markdown(
        f"""
<div class="card p-4 border-light shadow-sm mt-4" style="border-left: 4px solid {colors['text_main']} !important; border-radius: 8px; background-color: #ffffff;">
    <div class="d-flex gap-3 text-secondary font-sans" style="font-size: 13px; line-height: 1.6;">
        <div>
            <strong class="text-dark d-block mb-1 uppercase text-uppercase" style="font-size: 12px; font-weight: 700; letter-spacing: -0.01em;">Importante: Atencao Basica e Cobertura Vacinal</strong>
            Manter as taxas de cobertura acima de 95% e crucial para garantir a imunidade coletiva e evitar a reintroducao de doencas erradicadas. O acompanhamento continuado destes indicadores orienta acoes estrategicas de busca ativa pelas equipes de saude primaria.
        </div>
    </div>
</div>
        """,
        unsafe_allow_html=True
    )

except Exception as e:
    st.error(f"Erro ao processar dados de vacinacao: {e}")
