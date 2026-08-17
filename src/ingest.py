import sys
import os

# coloca a pasta raiz no path pra conseguir importar os modulos do src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingest_api import processar_e_salvar_dados
from src.database import criar_engine


def realizar_ingestao():
    print("Iniciando processo de ingestão de dados...")
    
    # conecta no banco e mostra qual ta usando
    _, db_type = criar_engine()
    print(f"Banco de dados ativo: {db_type.upper()}")
    
    try:
        processar_e_salvar_dados()
        print("\nSucesso! Todas as tabelas de arboviroses foram ingeridas com êxito da API pública.")
    except Exception as e:
        print(f"\nErro crítico durante a ingestão: {e}")
        sys.exit(1)


if __name__ == "__main__":
    realizar_ingestao()
