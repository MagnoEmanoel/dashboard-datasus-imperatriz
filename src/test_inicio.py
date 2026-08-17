import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api_client import consultar_cnes_estabelecimentos

def main():
    print("Fetching CNES data for Imperatriz (210530)...")
    df = consultar_cnes_estabelecimentos("210530")
    print("Fetched successfully. Row count:", len(df))
    print("\nColumns:", df.columns.tolist())
    
    # Mimic Início.py line 146
    cnes_exib = df[["codigo_cnes", "nome_fantasia", "descricao_esfera_administrativa", "descricao_turno_atendimento", "bairro_estabelecimento"]].copy()
    cnes_exib.columns = ["CNES", "Nome Fantasia", "Esfera Administrativa", "Turno de Atendimento", "Bairro"]
    
    print("\nSample rows:")
    print(cnes_exib.head(10))
    print("\nExporting to dict to test serialization...")
    d = cnes_exib.to_dict(orient="records")
    print("Serialized successfully. Records:", len(d))

if __name__ == "__main__":
    main()
