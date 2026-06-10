import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# carrega as credenciais do banco que estao no arquivo .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "datasus_imperatriz")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_SSLMODE = os.getenv("DB_SSLMODE", "")


def criar_engine():
    """
    Cria a conexao com o banco de dados.
    Primeiro tenta conectar no PostgreSQL (Neon DB).
    Se nao conseguir, usa um SQLite local pra nao travar o projeto.
    Retorna o engine e o tipo do banco que conectou.
    """
    # tenta conectar no PostgreSQL
    try:
        url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        if DB_SSLMODE:
            url += f"?sslmode={DB_SSLMODE}"
        engine = create_engine(url, connect_args={'connect_timeout': 5})
        # testa se o banco ta respondendo
        with engine.connect() as conn:
            pass
        return engine, "postgresql"
    except Exception as e:
        # se nao conectou no postgres, usa o sqlite local como alternativa
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "datasus_imperatriz.db"))
        url = f"sqlite:///{db_path}"
        engine = create_engine(url)
        return engine, "sqlite"


def salvar_tabela(df, nome_tabela):
    """Recebe um DataFrame do pandas e salva como tabela no banco."""
    engine, db_type = criar_engine()
    df.to_sql(nome_tabela, engine, if_exists="replace", index=False)
    print(f"[DB] Tabela '{nome_tabela}' salva no {db_type.upper()} com {len(df)} linhas.")


def carregar_tabela(nome_tabela):
    """Puxa uma tabela do banco e retorna como DataFrame do pandas."""
    import pandas as pd
    engine, _ = criar_engine()
    df = pd.read_sql_table(nome_tabela, engine)
    return df
