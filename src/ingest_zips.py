import zipfile
import os
import pandas as pd
import sys
import time
from sqlalchemy import text

# Coloca a pasta raiz no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.database import criar_engine

def clean_column_names(df):
    """Normaliza os nomes de colunas para minúsculo e sem caracteres especiais."""
    df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_").replace(".", "_") for c in df.columns]
    return df

def process_csv_file(zip_file, csv_name, file_size, engine, skip_estabelecimento=False):
    """Extrai e insere um arquivo CSV em blocos no PostgreSQL."""
    table_name = os.path.splitext(csv_name)[0].lower()
    # Remove sufixos de data comuns (ex: 202606 ou 202607) para manter tabelas com nomes limpos
    for suffix in ["202606", "202607", "2026", "2025"]:
        if table_name.endswith(suffix):
            table_name = table_name[:-len(suffix)]
    
    # Adiciona prefixo se começar com número
    if table_name[0].isdigit():
        table_name = "tb_" + table_name

    # Otimização: se for tbestabelecimento e já estiver carregado, pula
    if table_name == "tbestabelecimento" and skip_estabelecimento:
        print(f"  -> Tabela '{table_name}' já está populada no banco. Pulando re-importação.")
        return

    # Otimização de tamanho: pula tabelas secundárias gigantescas não utilizadas
    size_mb = file_size / (1024 * 1024)
    if size_mb > 15.0 and table_name != "tbestabelecimento":
        print(f"  -> Tabela '{table_name}' possui {size_mb:.1f} MB (maior que o limite de 15MB). Pulando para evitar sobrecarga...")
        return

    print(f"  -> Inserindo tabela '{table_name}' ({size_mb:.2f} MB) a partir de '{csv_name}'...")
    
    start_time = time.time()
    chunk_size = 20000
    first_chunk = True
    total_rows = 0
    
    # Abre o arquivo direto do ZIP
    with zip_file.open(csv_name) as f:
        # Usa pandas read_csv em chunks
        for chunk in pd.read_csv(f, sep=";", encoding="latin-1", chunksize=chunk_size, dtype=str, on_bad_lines="skip"):
            # Limpa e normaliza os dados do bloco
            chunk = clean_column_names(chunk)
            
            # Insere no banco
            if first_chunk:
                chunk.to_sql(name=table_name, con=engine, if_exists="replace", index=False)
                first_chunk = False
            else:
                chunk.to_sql(name=table_name, con=engine, if_exists="append", index=False)
            
            total_rows += len(chunk)
            
    duration = time.time() - start_time
    print(f"  [OK] Tabela '{table_name}' concluída! Total: {total_rows} linhas em {duration:.1f}s.")

def main():
    print("=== INGESTÃO AUTOMÁTICA DE ZIPS OTIMIZADA PARA NEON DB ===")
    
    # Conecta no Neon DB
    engine, db_type = criar_engine()
    print(f"Conectado com sucesso ao banco: {db_type.upper()}")
    
    # Verifica se tbestabelecimento já existe e está populada
    skip_estabelecimento = False
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT COUNT(*) FROM tbestabelecimento"))
            cnt = res.scalar()
            if cnt > 0:
                skip_estabelecimento = True
                print(f"Detectado: Tabela 'tbestabelecimento' já possui {cnt} registros.")
    except Exception:
        pass
        
    zips = [
        "COOPERCBO.ZIP", "CERTHOSPITALENSINOBRASIL.ZIP", "HOSPFILANTROPICOSBRASIL.ZIP",
        "GESTORFEDERAL_202607.ZIP", "GERENTEADMINCONTRATOS202607.ZIP", "ESTNATJURBRASIL202607.ZIP",
        "SAUDE_INDIGENA_202607.ZIP", "SAMUBRASIL_202607.ZIP", "EQUIPESBRASIL_202607.ZIP",
        "PROFISSIONAIS_BRASIL_AC_202607.ZIP", "BASE_DE_DADOS_CNES_202606.ZIP", "SCNES4840-COMPLETA.ZIP"
    ]
    
    workspace_dir = "/home/magno/unimed/dashboard-datasus-imperatriz"
    
    for z_name in zips:
        z_path = os.path.join(workspace_dir, z_name)
        if not os.path.exists(z_path):
            print(f"\n[Aviso] Arquivo {z_name} não encontrado no workspace. Pulando...")
            continue
            
        print(f"\n==========================================")
        print(f"Processando arquivo ZIP: {z_name}")
        print(f"==========================================")
        
        try:
            with zipfile.ZipFile(z_path) as z:
                # Filtra arquivos CSV
                csv_infos = [info for info in z.infolist() if info.filename.lower().endswith(".csv")]
                if not csv_infos:
                    print("  Não foram encontrados arquivos CSV neste ZIP (provavelmente instalador). Pulando...")
                    continue
                    
                print(f"Encontrados {len(csv_infos)} arquivos CSV no zip.")
                
                for info in csv_infos:
                    try:
                        process_csv_file(z, info.filename, info.file_size, engine, skip_estabelecimento)
                    except Exception as e:
                        print(f"  [Erro] Falha ao processar tabela '{info.filename}': {e}")
        except Exception as e:
            print(f"[Erro] Falha ao abrir ZIP '{z_name}': {e}")

    # Cria índice em tbestabelecimento se não existir
    print("\n--- Garantindo índice de otimização na tabela final ---")
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_cnes_mun ON tbestabelecimento (co_municipio_gestor)"))
            print("Índice 'idx_cnes_mun' validado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar índice: {e}")

    print("\n=== PROCESSO DE INGESTÃO CONCLUÍDO COM SUCESSO! ===")

if __name__ == "__main__":
    main()
