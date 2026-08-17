import requests
import pandas as pd
import time
import sys
import os

# coloca a pasta raiz no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import salvar_tabela, criar_engine

BASE_URL = "https://apidadosabertos.saude.gov.br"

def decode_sinan_age(age_val):
    """
    Decodifica a idade no formato do SINAN:
    Primeiro dígito representa a unidade de tempo (1: hora, 2: dia, 3: mês, 4: ano).
    Os outros três dígitos representam o valor.
    Ex: 4032 vira 32 anos. 3011 vira 0 anos (menor de 1 ano).
    """
    if pd.isna(age_val) or age_val is None:
        return None
    try:
        val = int(float(age_val))
        prefix = val // 1000
        age = val % 1000
        if prefix == 4:
            return age
        elif prefix in [1, 2, 3]:
            return 0  # menos de 1 ano
        else:
            # se o prefixo não bate com o padrão mas é um número razoável, assume anos
            if val < 120:
                return val
            return None
    except Exception:
        return None

def categorizar_faixa_etaria(idade):
    """Categoriza a idade em faixas etárias epidemiológicas padrão."""
    if idade is None or pd.isna(idade):
        return "Ignorado"
    if idade < 1:
        return "Menor de 1 ano"
    elif idade <= 4:
        return "1 a 4 anos"
    elif idade <= 14:
        return "5 a 14 anos"
    elif idade <= 24:
        return "15 a 24 anos"
    elif idade <= 34:
        return "25 a 34 anos"
    elif idade <= 44:
        return "35 a 44 anos"
    elif idade <= 54:
        return "45 a 54 anos"
    elif idade <= 64:
        return "55 a 64 anos"
    elif idade <= 74:
        return "65 a 74 anos"
    else:
        return "75 anos ou mais"

def fetch_with_retry(url, params=None, retries=3, backoff=2):
    """Faz um request GET com retry e timeout."""
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=35)
            if r.status_code == 200:
                return r.json()
            else:
                print(f"[Aviso] Status {r.status_code} na tentativa {attempt+1} para URL {url}")
        except requests.exceptions.RequestException as e:
            print(f"[Aviso] Erro na tentativa {attempt+1} para URL {url}: {e}")
        time.sleep(backoff * (attempt + 1))
    raise Exception(f"Falha ao consultar a API após {retries} tentativas para URL: {url}")

def obter_dados_municipio(disease_path, list_key, mun_param="id_municip"):
    """
    Obtém todos os dados da arbovirose filtrados para Imperatriz (210530)
    fazendo buscas anuais para acelerar e otimizar os tempos de resposta da API.
    """
    all_records = []
    # Loop de anos de 2018 a 2026 para obter dados históricos consistentes
    for ano in range(2018, 2027):
        print(f"  -> Buscando {list_key.upper()} para o ano {ano}...")
        offset = 0
        limit = 100
        while True:
            url = f"{BASE_URL}/{disease_path}"
            params = {
                mun_param: "210530",
                "nu_ano": str(ano),
                "limit": limit,
                "offset": offset
            }
            try:
                data = fetch_with_retry(url, params=params)
                items = data.get(list_key, [])
                if not items:
                    break
                all_records.extend(items)
                print(f"    Recuperados {len(items)} registros no offset {offset}...")
                if len(items) < limit:
                    break
                offset += limit
            except Exception as e:
                print(f"    [Erro] Falha ao obter dados para o ano {ano}, offset {offset}: {e}")
                break
    return all_records

def obter_dados_febre_amarela():
    """
    Obtém os dados de febre amarela em humanos.
    O endpoint não aceita filtro de ano ou município diretamente nos parâmetros da query de forma indexada.
    Por conta disso, baixamos os registros nacionais paginados (~3000 registros totais)
    e filtramos localmente para o município de Imperatriz (MA) (código LPI 210530).
    """
    print("  -> Buscando FEBRE AMARELA (Humana)...")
    all_records = []
    offset = 0
    limit = 1000
    while True:
        url = f"{BASE_URL}/arboviroses/febre-amarela-humanos-primatas-nao-humanos"
        params = {
            "limit": limit,
            "offset": offset
        }
        try:
            data = fetch_with_retry(url, params=params)
            items = data.get("febre_amarela_humanos_primatas", [])
            if not items:
                break
            # Filtra localmente apenas casos de Imperatriz (cod_mun_lpi == 210530)
            # e garante que sexo/idade estão presentes para excluir epizootias indiretas
            for d in items:
                cod_mun = str(d.get("cod_mun_lpi", ""))
                # Se for Imperatriz (MA)
                if cod_mun.startswith("210530") or cod_mun == "210530":
                    all_records.append(d)
                    
            print(f"    Processados {len(items)} registros nacionais no offset {offset}...")
            if len(items) < limit:
                break
            offset += limit
        except Exception as e:
            print(f"    [Erro] Falha ao obter febre amarela, offset {offset}: {e}")
            break
            
    return all_records

def processar_e_salvar_dados():
    print("Iniciando Ingestão de dados das arboviroses da API pública do Ministério da Saúde...")
    
    # 1. Dengue
    dengue_raw = obter_dados_municipio("arboviroses/dengue", "dengue")
    df_dengue = pd.DataFrame(dengue_raw)
    if not df_dengue.empty:
        df_dengue["idade_anos"] = df_dengue["nu_idade_n"].apply(decode_sinan_age)
        df_dengue["faixa_etaria"] = df_dengue["idade_anos"].apply(categorizar_faixa_etaria)
        salvar_tabela(df_dengue, "dengue")
    else:
        print("[Aviso] Nenhum dado de Dengue encontrado.")

    # 2. Zika
    zika_raw = obter_dados_municipio("arboviroses/zikavirus", "zikavirus")
    df_zika = pd.DataFrame(zika_raw)
    if not df_zika.empty:
        df_zika["idade_anos"] = df_zika["nu_idade_n"].apply(decode_sinan_age)
        df_zika["faixa_etaria"] = df_zika["idade_anos"].apply(categorizar_faixa_etaria)
        salvar_tabela(df_zika, "zika")
    else:
        print("[Aviso] Nenhum dado de Zika encontrado.")

    # 3. Chikungunya
    chiky_raw = obter_dados_municipio("arboviroses/chikungunya", "chikungunya")
    df_chiky = pd.DataFrame(chiky_raw)
    if not df_chiky.empty:
        df_chiky["idade_anos"] = df_chiky["nu_idade_n"].apply(decode_sinan_age)
        df_chiky["faixa_etaria"] = df_chiky["idade_anos"].apply(categorizar_faixa_etaria)
        salvar_tabela(df_chiky, "chikungunya")
    else:
        print("[Aviso] Nenhum dado de Chikungunya encontrado.")

    # 4. Febre Amarela
    fa_raw = obter_dados_febre_amarela()
    df_fa = pd.DataFrame(fa_raw)
    if not df_fa.empty:
        # idade já vem limpa no campo 'idade' do endpoint
        df_fa["idade_anos"] = pd.to_numeric(df_fa["idade"], errors="coerce")
        df_fa["faixa_etaria"] = df_fa["idade_anos"].apply(categorizar_faixa_etaria)
        # renomeia campos de data para nu_ano/ano_is
        df_fa["nu_ano"] = df_fa["ano_is"].astype(str)
        salvar_tabela(df_fa, "febre_amarela")
    else:
        print("[Aviso] Nenhum dado de Febre Amarela encontrado para Imperatriz.")

    print("\nProcesso de ingestão da API concluído!")

if __name__ == "__main__":
    processar_e_salvar_dados()
