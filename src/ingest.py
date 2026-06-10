import sys
import os

# coloca a pasta raiz no path pra conseguir importar os modulos do src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.load_data import (
    carregar_obitos_adultos,
    carregar_obitos_infantis,
    carregar_internacoes,
    carregar_sinasc,
    carregar_vacinacao
)
from src.database import salvar_tabela, criar_engine


def realizar_ingestao():
    print("Iniciando processo de ingestão de dados...")
    
    # conecta no banco e mostra qual ta usando
    _, db_type = criar_engine()
    print(f"Banco de dados ativo: {db_type.upper()}")
    
    try:
        # obitos de adultos (5 a 74 anos)
        print("Carregando óbitos de 5 a 74 anos...")
        df_obitos_adultos = carregar_obitos_adultos()
        salvar_tabela(df_obitos_adultos, "obitos_adultos")
        
        # obitos de criancas (menores de 5)
        print("Carregando óbitos infantis...")
        df_obitos_infantis = carregar_obitos_infantis()
        salvar_tabela(df_obitos_infantis, "obitos_infantis")
        
        # internacoes hospitalares
        print("Carregando internações...")
        df_internacoes = carregar_internacoes()
        salvar_tabela(df_internacoes, "internacoes")
        
        # nascidos vivos
        print("Carregando dados do SINASC...")
        df_sinasc = carregar_sinasc()
        salvar_tabela(df_sinasc, "sinasc_nascimentos")
        
        # vacinacao
        print("Carregando dados de vacinação...")
        df_vacinacao = carregar_vacinacao()
        salvar_tabela(df_vacinacao, "vacinacao_cobertura")
        
        print("\nSucesso! Todas as tabelas foram ingeridas com êxito.")
    except Exception as e:
        print(f"\nErro crítico durante a ingestão: {e}")
        sys.exit(1)


if __name__ == "__main__":
    realizar_ingestao()
