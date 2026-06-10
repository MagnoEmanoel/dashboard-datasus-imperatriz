import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "datasus_imperatriz")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


def criar_engine():
    """
    Tenta conectar ao PostgreSQL usando as credenciais do .env.
    Se a conexão falhar ou não estiver configurada, faz o fallback
    automático para um banco de dados local SQLite.
    
    Retorna uma tupla (engine, tipo_banco).
    """
    # 1. Tentar PostgreSQL
    try:
        url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(url, connect_args={'connect_timeout': 3})
        # Testar a conexão para ver se o banco está respondendo
        with engine.connect() as conn:
            pass
        return engine, "postgresql"
    except Exception as e:
        # Se falhar, faz o fallback para SQLite local
        # Colocamos o banco SQLite na raiz do projeto
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "datasus_imperatriz.db"))
        url = f"sqlite:///{db_path}"
        engine = create_engine(url)
        return engine, "sqlite"


def salvar_tabela(df, nome_tabela):
    """Salva um DataFrame como tabela no banco de dados (Postgres ou SQLite)."""
    engine, db_type = criar_engine()
    df.to_sql(nome_tabela, engine, if_exists="replace", index=False)
    print(f"[DB] Tabela '{nome_tabela}' salva no {db_type.upper()} com {len(df)} linhas.")


def carregar_tabela(nome_tabela):
    """Lê uma tabela do banco de dados (Postgres ou SQLite) e retorna como DataFrame."""
    import pandas as pd
    engine, _ = criar_engine()
    df = pd.read_sql_table(nome_tabela, engine)
    return df
