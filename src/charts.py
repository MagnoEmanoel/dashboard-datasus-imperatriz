import plotly.io as pio

# paleta de cores do projeto (tema claro e limpo)
COLORS = {
    "bg_main": "rgba(250, 249, 246, 0.4)", # fundo principal
    "bg_sidebar": "#ffffff",               # fundo da sidebar
    "bg_card": "#ffffff",                  # fundo dos cards
    "text_main": "#0f172a",                # texto principal escuro
    "text_muted": "#64748b",               # texto secundario cinza
    "text_accent": "#0f172a",              # texto destaque
    "border": "#f1f5f9",                   # borda dos elementos
    
    # cores de cada area do dashboard
    "mortalidade_adulto": "#0d9488",       # Teal
    "mortalidade_infantil": "#e11d48",     # Rose
    "internacoes": "#4f46e5",              # Indigo
    "nascimentos_emerald": "#10b981",      # Emerald
    "nascimentos_amber": "#f59e0b",        # Amber
    "vacinacao": "#0d9488",                 # Teal
    
    # nomes antigos que as paginas ainda usam
    "primary": "#0d9488",                  # Teal (mortalidade/vacinação)
    "secondary": "#4f46e5",                # Indigo (internações)
    "success": "#10b981",                  # Emerald (nascimentos)
    "danger": "#e11d48",                   # Rose (infantil)
    "warning": "#f59e0b",                  # Amber (nascimentos)
    "info": "#64748b",
    "neutral": "#64748b",
    
    # escala de cores pra graficos de calor
    "seq_blue": [
        "#ccfbf1", "#99f6e4", "#5eead4", "#2dd4bf", 
        "#0d9488", "#0f766e", "#115e59", "#134e4a"
    ],
    
    # cores pra graficos com varias categorias
    "categorical": [
        "#0d9488", "#4f46e5", "#10b981", "#e11d48", 
        "#f59e0b", "#06b6d4", "#2563eb", "#db2777"
    ]
}


def obter_paleta_cores():
    """Retorna as cores do projeto."""
    return COLORS


def aplicar_estilo_layout(fig, title="", x_title="", y_title="", hovermode="x unified"):
    """
    Aplica o visual padrao nos graficos do Plotly.
    Configura fontes, cores e formatacao pra ficar tudo no mesmo estilo.
    """
    fig.update_layout(
        template="plotly_white",
        title={
            "text": f"<b>{title}</b>",
            "y": 0.95,
            "x": 0.05,
            "xanchor": "left",
            "yanchor": "top",
            "font": {"size": 16, "family": "Inter, sans-serif", "color": COLORS["text_main"]}
        },
        hoverlabel={
            "bgcolor": COLORS["bg_card"],
            "font_size": 13,
            "font_family": "JetBrains Mono, monospace",
            "font_color": COLORS["text_main"],
            "bordercolor": COLORS["border"]
        },
        hovermode=hovermode,
        plot_bgcolor="rgba(0,0,0,0)",           # fundo transparente
        paper_bgcolor="rgba(0,0,0,0)",          # papel transparente
        margin=dict(l=40, r=30, t=65, b=40),
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.2,
            "xanchor": "center",
            "x": 0.5,
            "font": {"family": "Inter, sans-serif", "size": 11, "color": COLORS["text_muted"]},
            "bgcolor": "rgba(0,0,0,0)"
        }
    )

    # configura os eixos X e Y
    fig.update_xaxes(
        title_text=x_title,
        title_font={"family": "Inter, sans-serif", "size": 11, "color": COLORS["text_muted"]},
        tickfont={"family": "JetBrains Mono, monospace", "size": 10, "color": COLORS["text_muted"]},
        gridcolor=COLORS["border"],
        showline=True,
        linecolor=COLORS["border"],
        zeroline=False
    )
    
    fig.update_yaxes(
        title_text=y_title,
        title_font={"family": "Inter, sans-serif", "size": 11, "color": COLORS["text_muted"]},
        tickfont={"family": "JetBrains Mono, monospace", "size": 10, "color": COLORS["text_muted"]},
        gridcolor=COLORS["border"],
        showline=False,
        zeroline=True,
        zerolinecolor=COLORS["border"]
    )
    
    return fig


def injetar_custom_css():
    """CSS customizado pra deixar o Streamlit com a cara do projeto. Usa Bootstrap 5 pra ajudar no layout."""
    return f"""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
        
        /* reseta fontes e fundo geral do app */
        html, body, [class*="css"], [data-testid="stAppViewContainer"] {{
            font-family: 'Inter', sans-serif;
            background-color: #FAF9F6 !important; /* Off-white quente e acolhedor */
            color: {COLORS["text_main"]} !important;
        }}
        
        /* titulos */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            color: {COLORS["text_main"]} !important;
            letter-spacing: -0.02em;
        }}
        
        /* animacao de entrada suave */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* aplica a animacao nos blocos de conteudo */
        [data-testid="stVerticalBlock"] > div {{
            animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }}
        
        /* estilo dos cards de metricas */
        .metric-card {{
            background-color: {COLORS["bg_card"]};
            border-radius: 4px;
            padding: 18px;
            border: 1px solid {COLORS["border"]};
            border-left: 3px solid {COLORS["primary"]};
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .metric-card:hover {{
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border-color: #e2e8f0;
        }}
        .metric-title {{
            font-size: 11px;
            color: {COLORS["text_muted"]};
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .metric-value {{
            font-size: 24px;
            color: {COLORS["text_main"]};
            font-weight: 700;
            margin-top: 4px;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: -0.03em;
        }}
        .metric-subtitle {{
            font-size: 11px;
            color: {COLORS["text_muted"]};
            margin-top: 4px;
            font-family: 'Inter', sans-serif;
        }}
        
        /* sidebar */
        [data-testid="stSidebar"] {{
            background-color: {COLORS["bg_sidebar"]} !important;
            border-right: 1px solid {COLORS["border"]};
        }}
        [data-testid="stSidebar"] * {{
            color: {COLORS["text_main"]} !important;
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: {COLORS["text_main"]} !important;
        }}
        
        /* abas */
        button[data-baseweb="tab"] {{
            background-color: transparent !important;
            color: {COLORS["text_muted"]} !important;
            font-weight: 500 !important;
            border: none !important;
            font-family: 'Inter', sans-serif;
            font-size: 13px !important;
            padding: 8px 16px !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {COLORS["text_main"]} !important;
            border-bottom: 2px solid {COLORS["text_main"]} !important;
            font-weight: 600 !important;
        }}
        
        /* campos de selecao e filtros */
        div[data-baseweb="select"] > div {{
            background-color: #ffffff !important;
            border-color: #e2e8f0 !important;
            color: {COLORS["text_main"]} !important;
            border-radius: 4px !important;
            font-size: 13px !important;
        }}
        div[role="listbox"] {{
            background-color: #ffffff !important;
            color: {COLORS["text_main"]} !important;
            font-size: 13px !important;
        }}
        
        /* slider de anos */
        div[data-testid="stSlider"] {{
            font-family: 'JetBrains Mono', monospace !important;
        }}
        
        /* tabelas de dados */
        div[data-testid="stDataFrame"] {{
            background-color: #ffffff !important;
            border: 1px solid {COLORS["border"]} !important;
            border-radius: 4px;
        }}
        
        /* notas e citacoes */
        blockquote {{
            background-color: #ffffff !important;
            border-left: 3px solid {COLORS["text_muted"]} !important;
            color: {COLORS["text_muted"]} !important;
            padding: 10px 14px !important;
            margin: 10px 0 !important;
            border-radius: 4px !important;
            border: 1px solid {COLORS["border"]};
            border-left-width: 3px;
        }}
        blockquote p {{
            color: {COLORS["text_muted"]} !important;
            margin: 0 !important;
            font-size: 12px !important;
            line-height: 1.5 !important;
        }}
        
        /* caixas de informacao */
        .stInfo, div[data-testid="stNotification"] {{
            background-color: #ffffff !important;
            border: 1px solid {COLORS["border"]} !important;
            color: {COLORS["text_muted"]} !important;
            border-left: 3px solid {COLORS["text_muted"]} !important;
            font-size: 12px !important;
        }}
        
        /* botoes */
        .stButton>button {{
            background-color: #ffffff;
            color: {COLORS["text_main"]};
            border-radius: 4px;
            border: 1px solid #cbd5e1;
            padding: 6px 12px;
            font-weight: 500;
            font-size: 13px;
            transition: all 0.15s ease;
        }}
        .stButton>button:hover {{
            background-color: #f8fafc;
            border-color: #94a3b8;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }}
    </style>
    """
