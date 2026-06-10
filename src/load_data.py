import pandas as pd
import os

# caminho da pasta com os CSV originais
DATA_RAW = os.path.join("data", "raw")


def ler_csv_limpo(caminho, col_index_name):
    """
    Le e limpa os arquivos CSV que foram exportados do DATASUS.
    Os CSV do TabNet vem com separador ';', encoding latin1,
    linhas de rodape com notas tecnicas e numeros no formato BR.
    Essa funcao trata tudo isso e devolve um DataFrame limpo.
    """
    if not os.path.exists(caminho):
        # tenta achar o arquivo se o script foi rodado de outra pasta
        caminho_alternativo = os.path.join("..", caminho)
        if os.path.exists(caminho_alternativo):
            caminho = caminho_alternativo
        else:
            raise FileNotFoundError(f"Arquivo não encontrado em: {caminho}")
            
    df = pd.read_csv(caminho, sep=";", encoding="latin1", engine="python")
    
    # tira espacos extras dos nomes das colunas
    df.columns = [c.strip() for c in df.columns]
    
    # pega o nome da primeira coluna
    first_col = df.columns[0]
    
    # tira linhas onde a primeira coluna ta vazia
    df = df.dropna(subset=[first_col])
    
    # transforma a primeira coluna em texto pra poder filtrar
    df[first_col] = df[first_col].astype(str).str.strip()
    
    # remove as linhas de notas e fontes que o DATASUS coloca no rodape
    df = df[~df[first_col].str.startswith("Fonte:", na=False)]
    df = df[~df[first_col].str.startswith("Nota:", na=False)]
    df = df[~df[first_col].str.startswith("Notas:", na=False)]
    df = df[~df[first_col].str.startswith("1. O total", na=False)] # observações comuns
    
    # remove linhas vazias que sobraram
    df = df[df[first_col] != ""]
    
    # tira a linha de Total que o TabNet sempre coloca
    df = df[df[first_col].str.lower() != "total"]
    
    # renomeia a primeira coluna pro nome padrao que a gente quer
    df = df.rename(columns={first_col: col_index_name})
    
    # agora trata as colunas numericas
    for col in df.columns:
        if col != col_index_name:
            # converte pra string pra poder limpar os caracteres
            col_str = df[col].astype(str).str.strip()
            
            # tira os pontos de milhar (ex: '1.250' vira '1250')
            col_str = col_str.str.replace(".", "", regex=False)
            
            # no DATASUS o '-' significa zero
            col_str = col_str.str.replace("-", "0", regex=False)
            
            # troca virgula por ponto pra funcionar como decimal
            col_str = col_str.str.replace(",", ".", regex=False)
            
            # converte pra numero, se der erro coloca 0
            df[col] = pd.to_numeric(col_str, errors="coerce").fillna(0)
            
            # se eh coluna de ano ou so tem inteiro, converte pra int
            if col.isdigit() or df[col].round().eq(df[col]).all():
                df[col] = df[col].astype(int)
                
    return df


def carregar_obitos_adultos():
    """Carrega os obitos evitaveis de 5 a 74 anos do SIM."""
    caminho = os.path.join(DATA_RAW, "obitos_evitaveis_5_a_74.csv")
    return ler_csv_limpo(caminho, "causa")


def carregar_obitos_infantis():
    """Carrega os obitos evitaveis de menores de 5 anos."""
    caminho = os.path.join(DATA_RAW, "obitos_evitaveis_5.csv")
    return ler_csv_limpo(caminho, "causa")


def carregar_internacoes():
    """Carrega as internacoes por capitulo CID-10 do SIH."""
    caminho = os.path.join(DATA_RAW, "sih_internacoes.csv")
    return ler_csv_limpo(caminho, "capitulo_cid")


def carregar_sinasc():
    """Carrega nascidos vivos por faixa etaria da mae do SINASC."""
    caminho = os.path.join(DATA_RAW, "sinasc_maes.csv")
    return ler_csv_limpo(caminho, "faixa_etaria_mae")


def carregar_vacinacao():
    """Carrega a cobertura vacinal por ano do SI-PNI."""
    caminho = os.path.join(DATA_RAW, "vacinacao.csv")
    return ler_csv_limpo(caminho, "ano")
