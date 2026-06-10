import pandas as pd
import os

# Base path for raw data
DATA_RAW = os.path.join("data", "raw")


def ler_csv_limpo(caminho, col_index_name):
    """
    Carrega e limpa arquivos CSV exportados do DATASUS (TabNet/TABWIN).
    
    Características do tratamento:
    - Lê com separador ';' e encoding 'latin1'.
    - Remove linhas nulas ou vazias.
    - Filtra rodapés típicos do DATASUS (linhas que começam com 'Fonte' ou 'Nota').
    - Remove a linha de 'Total'.
    - Trata números no formato brasileiro (ex: '1.250' -> 1250, ',' para '.' e '-' para '0').
    """
    if not os.path.exists(caminho):
        # Fallback para caso o script seja rodado de dentro da pasta 'src' ou 'pages'
        caminho_alternativo = os.path.join("..", caminho)
        if os.path.exists(caminho_alternativo):
            caminho = caminho_alternativo
        else:
            raise FileNotFoundError(f"Arquivo não encontrado em: {caminho}")
            
    df = pd.read_csv(caminho, sep=";", encoding="latin1", engine="python")
    
    # Limpa espaços nas colunas e linhas
    df.columns = [c.strip() for c in df.columns]
    
    # Descobre a primeira coluna
    first_col = df.columns[0]
    
    # Remove linhas onde a primeira coluna é nula
    df = df.dropna(subset=[first_col])
    
    # Converte a primeira coluna para string para aplicar filtros de texto
    df[first_col] = df[first_col].astype(str).str.strip()
    
    # Filtra linhas de notas técnicas e fontes do DATASUS
    df = df[~df[first_col].str.startswith("Fonte:", na=False)]
    df = df[~df[first_col].str.startswith("Nota:", na=False)]
    df = df[~df[first_col].str.startswith("Notas:", na=False)]
    df = df[~df[first_col].str.startswith("1. O total", na=False)] # observações comuns
    
    # Filtra linhas que sejam totalmente vazias ou contendo apenas hifens/traços na primeira coluna
    df = df[df[first_col] != ""]
    
    # Remove linha "Total" (case insensitive)
    df = df[df[first_col].str.lower() != "total"]
    
    # Renomeia a primeira coluna para o nome padrão solicitado
    df = df.rename(columns={first_col: col_index_name})
    
    # Trata colunas de dados (numéricas)
    for col in df.columns:
        if col != col_index_name:
            # Converte a coluna para string para podermos limpar
            col_str = df[col].astype(str).str.strip()
            
            # Remove pontos de milhares (ex: '1.250' -> '1250')
            col_str = col_str.str.replace(".", "", regex=False)
            
            # Substitui o hífen '-' por '0' (representação do DATASUS para valor zerado)
            col_str = col_str.str.replace("-", "0", regex=False)
            
            # Substitui vírgula por ponto para valores decimais
            col_str = col_str.str.replace(",", ".", regex=False)
            
            # Converte para numérico. Se falhar, preenche com 0
            df[col] = pd.to_numeric(col_str, errors="coerce").fillna(0)
            
            # Se for coluna de ano ou se todos forem inteiros, converte para int
            if col.isdigit() or df[col].round().eq(df[col]).all():
                df[col] = df[col].astype(int)
                
    return df


def carregar_obitos_adultos():
    """Carrega óbitos evitáveis de 5 a 74 anos (SIM)."""
    caminho = os.path.join(DATA_RAW, "obitos_evitaveis_5_a_74.csv")
    return ler_csv_limpo(caminho, "causa")


def carregar_obitos_infantis():
    """Carrega óbitos evitáveis menores de 5 anos (SIM infantil)."""
    caminho = os.path.join(DATA_RAW, "obitos_evitaveis_5.csv")
    return ler_csv_limpo(caminho, "causa")


def carregar_internacoes():
    """Carrega internações hospitalares por capítulo CID-10 (SIH)."""
    caminho = os.path.join(DATA_RAW, "sih_internacoes.csv")
    return ler_csv_limpo(caminho, "capitulo_cid")


def carregar_sinasc():
    """Carrega nascidos vivos por faixa etária da mãe (SINASC)."""
    caminho = os.path.join(DATA_RAW, "sinasc_maes.csv")
    return ler_csv_limpo(caminho, "faixa_etaria_mae")


def carregar_vacinacao():
    """Carrega cobertura vacinal por ano e imunobiológico (SI-PNI)."""
    caminho = os.path.join(DATA_RAW, "vacinacao.csv")
    return ler_csv_limpo(caminho, "ano")
