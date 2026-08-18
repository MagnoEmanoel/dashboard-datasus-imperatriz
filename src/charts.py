import plotly.io as pio

# paleta de cores do projeto (Streamlit Design System - Figma Specs)
COLORS = {
    "bg_main": "#f8fafc",                  # fundo principal limpo
    "bg_sidebar": "#ffffff",               # fundo da sidebar
    "bg_card": "#ffffff",                  # fundo dos cards
    "text_main": "#31333f",                # texto principal oficial do Streamlit
    "text_muted": "#808495",               # texto secundario cinza
    "text_accent": "#111827",              # texto destaque
    "border": "#e6e8eb",                   # borda dos elementos

    # cores oficiais do Streamlit Design System
    "primary": "#ff4b4b",                  # Streamlit Coral/Red
    "secondary": "#1c83e1",                # Streamlit Blue
    "success": "#00d4b1",                  # Emerald
    "danger": "#ff4b4b",                   # Coral
    "warning": "#ffbd45",                  # Amber
    "info": "#1c83e1",                     # Blue

    # cores por area funcional
    "mortalidade_adulto": "#00c0f2",       # Cyan
    "mortalidade_infantil": "#ff4b4b",     # Coral
    "internacoes": "#1c83e1",              # Blue
    "nascimentos_emerald": "#00d4b1",      # Emerald
    "nascimentos_amber": "#ffbd45",        # Amber
    "vacinacao": "#ff4b4b",                 # Coral

    # escala de cores pra graficos
    "seq_blue": [
        "#ffeae8", "#ffc7c2", "#ff9b93", "#ff6d63",
        "#ff4b4b", "#d93838", "#b32727", "#8c1818"
    ],

    # cores para categorias (Streamlit Design System Palette)
    "categorical": [
        "#ff4b4b", "#1c83e1", "#00d4b1", "#ffbd45",
        "#7d3ac1", "#00c0f2", "#e03131", "#2b8a3e"
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
        autosize=True,
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
        zerolinecolor=COLORS["border"],
        automargin=True
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
            background-color: {COLORS["bg_main"]} !important;
            color: {COLORS["text_main"]} !important;
        }}

        /* chrome do Streamlit no mesmo tema claro */
        [data-testid="stHeader"], [data-testid="stToolbar"],
        [data-testid="stDecoration"], [data-testid="stStatusWidget"] {{
            background: {COLORS["bg_main"]} !important;
            background-image: none !important;
        }}
        [data-testid="stMainBlockContainer"] {{ background: transparent !important; }}

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

        /* estilo dos cards de metricas (Streamlit Design System Figma) */
        .metric-card {{
            background-color: {COLORS["bg_card"]};
            border-radius: 8px;
            padding: 20px;
            border: 1px solid {COLORS["border"]};
            border-top: 3px solid {COLORS["primary"]};
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03);
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .metric-card:hover {{
            box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.08), 0 2px 6px -1px rgba(0, 0, 0, 0.04);
            border-color: #cbd5e1;
            transform: translateY(-1px);
        }}
        .metric-title {{
            font-size: 12px;
            color: {COLORS["text_muted"]};
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .metric-value {{
            font-size: 26px;
            color: {COLORS["text_main"]};
            font-weight: 700;
            margin-top: 6px;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: -0.03em;
        }}
        .metric-subtitle {{
            font-size: 12px;
            color: {COLORS["text_muted"]};
            margin-top: 6px;
            font-family: 'Inter', sans-serif;
        }}

        /* Streamlit Native Tabs Component (Figma SDS style) */
        button[data-baseweb="tab"] {{
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            color: {COLORS["text_muted"]} !important;
            border-bottom: 2px solid transparent !important;
            padding: 8px 16px !important;
            transition: all 0.15s ease !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {COLORS["primary"]} !important;
            font-weight: 600 !important;
            border-bottom-color: {COLORS["primary"]} !important;
            background: transparent !important;
        }}

        /* Streamlit Buttons (SDS style) */
        .stButton > button {{
            border-radius: 8px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            border: 1px solid {COLORS["border"]} !important;
            transition: all 0.15s ease !important;
        }}
        .stButton > button:hover {{
            border-color: {COLORS["primary"]} !important;
            color: {COLORS["primary"]} !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        }}

        /* Callouts & Alert Boxes (Figma SDS style) */
        [data-testid="stAlert"] {{
            border-radius: 8px !important;
            border: 1px solid #d0e8f2 !important;
            background-color: #e8f4f8 !important;
            color: #1e3a8a !important;
            padding: 12px 16px !important;
            font-family: 'Inter', sans-serif !important;
        }}

        /* Sliders (Streamlit Red accent) */
        [data-baseweb="slider"] [role="slider"] {{
            background-color: {COLORS["primary"]} !important;
            border-color: {COLORS["primary"]} !important;
        }}
        [data-baseweb="slider"] div[style*="background-color"] {{
            background-color: {COLORS["primary"]} !important;
        }}

        /* Streamlit Dataframe & Table Styling (Clean Light Theme) */
        [data-testid="stDataFrame"], [data-testid="stTable"] {{
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
        }}

        /* ============ SIDEBAR / NAVEGAÇÃO ============ */
        [data-testid="stSidebar"] {{
            background-color: {COLORS["bg_sidebar"]} !important;
            background-image: none !important;
            border-right: 1px solid {COLORS["border"]};
            box-shadow: none !important;
        }}
        section[data-testid="stSidebar"] {{
            background: {COLORS["bg_sidebar"]} !important;
            background-image: none !important;
            box-shadow: none !important;
        }}
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavItems"] {{
            background-color: {COLORS["bg_sidebar"]} !important;
            background-image: none !important;
            -webkit-mask-image: none !important;
            mask-image: none !important;
            box-shadow: none !important;
        }}
        section[data-testid="stSidebar"]::before,
        section[data-testid="stSidebar"]::after,
        [data-testid="stSidebar"]::before,
        [data-testid="stSidebar"]::after,
        [data-testid="stSidebar"] > div::before,
        [data-testid="stSidebar"] > div::after,
        [data-testid="stSidebarContent"]::before,
        [data-testid="stSidebarContent"]::after,
        [data-testid="stSidebarNav"]::after,
        [data-testid="stSidebarNavItems"]::before,
        [data-testid="stSidebarNavItems"]::after {{
            content: none !important;
            display: none !important;
            background: transparent !important;
            background-image: none !important;
            box-shadow: none !important;
            border: 0 !important;
        }}
        [data-testid="stSidebarContent"] {{
            overflow: visible !important;
        }}
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavItems"] {{
            position: relative !important;
            isolation: isolate !important;
        }}
        [data-testid="stSidebar"] * {{
            color: {COLORS["text_main"]} !important;
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: {COLORS["text_main"]} !important;
        }}

        /* container da lista de páginas (menu lateral gerado pelo Streamlit) */
        [data-testid="stSidebarNav"] {{
            padding-top: 0.5rem;
        }}
        [data-testid="stSidebarNav"]::before {{
            content: "PAINEL DATASUS";
            display: block;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.16em;
            color: {COLORS["text_muted"]};
            text-transform: uppercase;
            margin: 0.9rem 1rem 0.4rem;
            font-family: 'Inter', sans-serif;
        }}

        /* lista de navegação */
        [data-testid="stSidebarNavItems"] {{
            padding: 0.2rem 0.6rem !important;
        }}
        [data-testid="stSidebarNavItems"] ul {{
            gap: 3px !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }}
        [data-testid="stSidebarNavItems"] ul li {{
            border-radius: 8px !important;
            transition: background-color 0.15s ease, transform 0.1s ease;
            margin-bottom: 1px !important;
        }}
        [data-testid="stSidebarNavItems"] ul li:hover {{
            background-color: #f2f5f9 !important;
        }}

        /* link de navegação */
        [data-testid="stSidebarNavLink"] {{
            border-radius: 8px !important;
            padding: 0.5rem 0.75rem !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13.5px !important;
            font-weight: 500 !important;
            color: {COLORS["text_main"]} !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.6rem !important;
            text-decoration: none !important;
            position: relative !important;
            transition: color 0.15s ease, background-color 0.15s ease;
            outline: none !important;
            box-shadow: none !important;
        }}
        [data-testid="stSidebarNavLink"]:focus, [data-testid="stSidebarNavLink"]:focus-visible, [data-testid="stSidebarNavLink"]:focus-within {{
            outline: none !important;
            box-shadow: none !important;
            border: none !important;
        }}
        [data-testid="stSidebarNavLink"]::before {{
            content: "";
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #cbd5e1;
            flex-shrink: 0;
            transition: background-color 0.15s ease, transform 0.15s ease;
        }}
        [data-testid="stSidebarNavLink"]:hover {{
            color: {COLORS["primary"]} !important;
            background-color: transparent !important;
        }}
        [data-testid="stSidebarNavLink"]:hover::before {{
            background-color: {COLORS["primary"]} !important;
            transform: scale(1.15);
        }}

        /* texto do item do menu */
        [data-testid="stSidebarNavLink"] span {{
            white-space: normal !important;
            line-height: 1.3 !important;
        }}

        /* página ativa (marcada via JS que injeta aria-current="page") */
        [data-testid="stSidebarNavLink"][aria-current="page"] {{
            color: {COLORS["primary"]} !important;
            font-weight: 600 !important;
            background: #ecfdf5 !important;
            background-image: none !important;
        }}
        [data-testid="stSidebarNavLink"][aria-current="page"]::before {{
            background-color: {COLORS["primary"]} !important;
            box-shadow: none !important;
        }}
        li:has([data-testid="stSidebarNavLink"][aria-current="page"]) {{
            background: transparent !important;
            border-left: 3px solid {COLORS["primary"]} !important;
            border-radius: 4px !important;
        }}

        /* remove contorno/realce padrão ao clicar em qualquer elemento do menu */
        [data-testid="stSidebarNav"] * {{
            outline: none !important;
            box-shadow: none !important;
        }}
        [data-testid="stSidebar"] *:focus, [data-testid="stSidebar"] *:focus-visible {{
            outline: none !important;
            box-shadow: none !important;
        }}

        /* submenu (itens aninhados) */
        [data-testid="stSidebarNavItems"] ul ul {{
            margin-left: 0.3rem !important;
            border-left: 1px solid {COLORS["border"]};
            padding-left: 0.4rem !important;
        }}

        /* separador e botão de recolher/expandir */
        [data-testid="stSidebarNavSeparator"] {{
            margin: 0.4rem 0.6rem !important;
        }}
        [data-testid="stSidebarNavExpandIcon"] {{
            color: {COLORS["text_muted"]} !important;
        }}

        /* rodapé da sidebar: texto informativo */
        [data-testid="stSidebar"] hr {{
            margin: 0.6rem 0.5rem !important;
            border-color: {COLORS["border"]} !important;
        }}

        /* títulos de seção dos filtros (ex: "### Filtros Globais") */
        [data-testid="stSidebar"] h3 {{
            font-size: 13px !important;
            font-weight: 600 !important;
            letter-spacing: 0.06em !important;
            text-transform: uppercase !important;
            color: {COLORS["text_muted"]} !important;
            padding: 0.2rem 0.3rem 0.4rem;
            margin-bottom: 0.2rem !important;
            border-bottom: 1px solid {COLORS["border"]};
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        [data-testid="stSidebar"] h3::before {{
            content: "";
            width: 3px;
            height: 14px;
            background: {COLORS["primary"]};
            border-radius: 2px;
            display: inline-block;
        }}

        /* rótulos dos filtros (selectbox, checkbox, etc.) */
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
            font-size: 12px !important;
            font-weight: 500 !important;
            color: {COLORS["text_muted"]} !important;
        }}
        [data-testid="stSidebar"] label p {{
            font-size: 12px !important;
            font-weight: 500 !important;
            color: {COLORS["text_muted"]} !important;
        }}

        /* cabeçalho da sidebar expandida */
        [data-testid="stSidebarHeader"] {{
            padding: 0.6rem 1rem 0.2rem;
            background: {COLORS["bg_sidebar"]} !important;
            border-bottom: 1px solid {COLORS["border"]};
            box-shadow: none !important;
        }}

        /* Plotly: fullscreen ocupa a tela e recalcula o gráfico */
        [data-testid="stFullScreenFrame"] {{
            background: {COLORS["bg_main"]} !important;
            padding: 1rem !important;
            overflow: hidden !important;
        }}
        [data-testid="stFullScreenFrame"] [data-testid="stPlotlyChart"],
        [data-testid="stFullScreenFrame"] .js-plotly-plot,
        [data-testid="stFullScreenFrame"] .plot-container,
        [data-testid="stFullScreenFrame"] .svg-container {{
            width: 100% !important;
            height: 100% !important;
            min-height: calc(100vh - 2rem) !important;
        }}
        [data-testid="stFullScreenFrame"] .modebar {{
            background: transparent !important;
        }}

        /* toolbar dos elementos (fullscreen, menu, etc.) */
        [data-testid="stElementToolbar"] {{
            position: absolute !important;
            top: 8px !important;
            right: 8px !important;
            margin: 0 !important;
            opacity: 1 !important;
            visibility: visible !important;
            display: flex !important;
            align-items: center !important;
            gap: 4px !important;
            padding: 4px !important;
            border-radius: 7px !important;
            background: rgba(248, 250, 252, 0.96) !important;
            border: 1px solid rgba(203, 213, 225, 0.9) !important;
            box-shadow: 0 3px 10px rgba(15, 23, 42, 0.12) !important;
            overflow: visible !important;
            z-index: 20 !important;
            width: fit-content !important;
            height: fit-content !important;
        }}
        [data-testid="stElementToolbar"] > div {{
            display: flex !important;
            align-items: center !important;
            gap: 4px !important;
        }}
        [data-testid="stTooltipHoverTarget"] {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}
        [data-testid="stElementToolbar"] button {{
            width: 26px !important;
            height: 26px !important;
            min-width: 26px !important;
            min-height: 26px !important;
            padding: 4px !important;
            border-radius: 6px !important;
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            color: #0f172a !important;
            box-shadow: none !important;
        }}
        [data-testid="stElementToolbar"] button:hover {{
            background: #ecfdf5 !important;
            color: {COLORS["primary"]} !important;
            border-color: rgba(13, 148, 136, 0.35) !important;
        }}
        [data-testid="stElementToolbar"] button:focus,
        [data-testid="stElementToolbar"] button:focus-visible {{
            outline: 2px solid rgba(13, 148, 136, 0.22) !important;
            outline-offset: 2px !important;
        }}
        [data-testid="stElementToolbar"] button svg,
        [data-testid="stElementToolbarButton"] svg {{
            color: currentColor !important;
            display: block !important;
        }}
        [data-testid="stElementToolbar"] button svg {{
            width: 15px !important;
            height: 15px !important;
        }}
        [role="tooltip"] {{
            display: none !important;
            opacity: 0 !important;
            visibility: hidden !important;
        }}

        /* garante contraste da toolbar sobre tabelas escuras */
        div[data-testid="stDataFrame"] [data-testid="stElementToolbar"] {{
            opacity: 1 !important;
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
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {{
            background-color: #ffffff !important;
            border-color: #e2e8f0 !important;
            border-radius: 8px !important;
            font-size: 13px !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }}
        [data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {{
            border-color: #94a3b8 !important;
        }}
        [data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {{
            border-color: {COLORS["primary"]} !important;
            box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.12) !important;
        }}
        [data-testid="stSidebar"] div[data-baseweb="select"] > div > div {{
            color: {COLORS["text_main"]} !important;
        }}
        div[role="listbox"] {{
            background-color: #ffffff !important;
            color: {COLORS["text_main"]} !important;
            font-size: 13px !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
            border: 1px solid {COLORS["border"]} !important;
        }}
        div[role="option"] {{
            border-radius: 6px !important;
            margin: 0 4px !important;
            padding: 6px 10px !important;
            font-size: 13px !important;
        }}
        div[role="option"]:hover, div[role="option"][aria-selected="true"] {{
            background-color: rgba(13, 148, 136, 0.08) !important;
            color: {COLORS["primary"]} !important;
        }}

        /* checkbox da sidebar */
        [data-testid="stSidebar"] [data-testid="stCheckbox"] span[data-baseweb="checkbox"] {{
            border-radius: 4px !important;
            border-color: #cbd5e1 !important;
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
    <script>
        // Marca o item ativo no menu lateral comparando o href com a URL atual.
        // O Streamlit não injeta aria-current por padrão, então fazemos aqui.
        function marcarMenuAtivo() {{
            var links = document.querySelectorAll('a[data-testid="stSidebarNavLink"]');
            var caminho = window.location.pathname;
            try {{ caminho = decodeURIComponent(caminho); }} catch (e) {{}}
            links.forEach(function(link) {{
                var href = link.getAttribute('href') || '';
                var alvo = '';
                try {{
                    alvo = new URL(href, window.location.origin).pathname;
                    alvo = decodeURIComponent(alvo);
                }} catch (e) {{}}
                if (caminho === alvo) {{
                    link.setAttribute('aria-current', 'page');
                }} else {{
                    link.removeAttribute('aria-current');
                }}
            }});
        }}
        // executa após o carregamento e em intervalos (a nav é renderizada por JS)
        marcarMenuAtivo();
        setInterval(marcarMenuAtivo, 500);
    </script>
    """
