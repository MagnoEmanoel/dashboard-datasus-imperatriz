import sys
import os

# Adiciona o diretório raiz ao PYTHONPATH para facilitar importações
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
    
    # Executa a conexão e exibe qual banco está sendo utilizado
    _, db_type = criar_engine()
    print(f"Banco de dados ativo: {db_type.upper()}")
    
    try:
        # 1. Óbitos Adultos (5 a 74 anos)
        print("Carregando óbitos de 5 a 74 anos...")
        df_obitos_adultos = carregar_obitos_adultos()
        salvar_tabela(df_obitos_adultos, "obitos_adultos")
        
        # 2. Óbitos Infantis (menores de 5 anos)
        print("Carregando óbitos infantis...")
        df_obitos_infantis = carregar_obitos_infantis()
        salvar_tabela(df_obitos_infantis, "obitos_infantis")
        
        # 3. Internações (SIH)
        print("Carregando internações...")
        df_internacoes = carregar_internacoes()
        salvar_tabela(df_internacoes, "internacoes")
        
        # 4. Nascidos Vivos (SINASC)
        print("Carregando dados do SINASC...")
        df_sinasc = carregar_sinasc()
        salvar_tabela(df_sinasc, "sinasc_nascimentos")
        
        # 5. Vacinação (SI-PNI)
        print("Carregando dados de vacinação...")
        df_vacinacao = carregar_vacinacao()
        salvar_tabela(df_vacinacao, "vacinacao_cobertura")
        
        print("\nSucesso! Todas as tabelas foram ingeridas com êxito.")
    except Exception as e:
        print(f"\nErro crítico durante a ingestão: {e}")
        sys.exit(1)


if __name__ == "__main__":
    realizar_ingestao()
