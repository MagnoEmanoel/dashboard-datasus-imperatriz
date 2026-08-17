import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import criar_engine
from sqlalchemy import text

def main():
    engine, db_type = criar_engine()
    print("Conectado ao banco:", db_type.upper())
    
    # 1. Tabelas antigas para apagar
    tabelas_antigas = [
        "obitos_adultos", "obitos_infantis", "internacoes", 
        "sinasc_nascimentos", "vacinacao_cobertura"
    ]
    
    with engine.connect() as conn:
        print("\n--- Apagando tabelas antigas ---")
        for tab in tabelas_antigas:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS \"{tab}\" CASCADE"))
                print(f"Tabela '{tab}' apagada com sucesso!")
            except Exception as e:
                print(f"Erro ao apagar '{tab}': {e}")
                
        # 2. Criando índice na coluna co_municipio_gestor para buscas instantâneas
        print("\n--- Criando índice de otimização ---")
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_cnes_mun ON tbestabelecimento (co_municipio_gestor)"))
            print("Índice 'idx_cnes_mun' criado com sucesso!")
        except Exception as e:
            print(f"Erro ao criar índice: {e}")
            
        # 3. Listando colunas e conferindo se há dados de Imperatriz
        print("\n--- Listando colunas da tabela tbestabelecimento ---")
        try:
            res_cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'tbestabelecimento'"))
            cols = [r[0] for r in res_cols]
            print("Colunas:", cols)
            
            res_sample = conn.execute(text("SELECT no_fantasia, co_municipio_gestor FROM tbestabelecimento WHERE co_municipio_gestor = '210530' LIMIT 3"))
            print("\nAmostra de Imperatriz:")
            for row in res_sample:
                print("-", row[0], "| mun =", row[1])
        except Exception as e:
            print(f"Erro ao listar dados: {e}")

if __name__ == "__main__":
    main()
