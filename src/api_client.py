import streamlit as st
import requests
import pandas as pd

BASE_URL = "https://apidadosabertos.saude.gov.br"

@st.cache_data(ttl=3600, show_spinner=False)  # cache de 1 hora para a lista de municípios
def obter_estados_municipios():
    """
    Consome a API de Localidades do IBGE para obter a lista completa de estados
    e municípios do Brasil de forma extremamente rápida.
    """
    try:
        r = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/municipios", timeout=15)
        if r.status_code == 200:
            data = r.json()
            municipios_por_uf = {}
            for item in data:
                if not item or not isinstance(item, dict):
                    continue
                
                uf_sigla = None
                
                # Tenta pelo caminho padrão microrregiao -> mesorregiao -> UF
                microrregiao = item.get("microrregiao")
                if isinstance(microrregiao, dict):
                    mesorregiao = microrregiao.get("mesorregiao")
                    if isinstance(mesorregiao, dict):
                        uf = mesorregiao.get("UF")
                        if isinstance(uf, dict):
                            uf_sigla = uf.get("sigla")
                
                # Se não achou, tenta pelo caminho regiao-imediata -> regiao-intermediaria -> UF
                if not uf_sigla:
                    regiao_imediata = item.get("regiao-imediata")
                    if isinstance(regiao_imediata, dict):
                        regiao_intermediaria = regiao_imediata.get("regiao-intermediaria")
                        if isinstance(regiao_intermediaria, dict):
                            uf = regiao_intermediaria.get("UF")
                            if isinstance(uf, dict):
                                uf_sigla = uf.get("sigla")
                
                # Fallback: tenta deduzir pelos 2 primeiros dígitos do ID do município
                if not uf_sigla:
                    mun_id_str = str(item.get("id", ""))
                    if len(mun_id_str) >= 2:
                        codigo_uf = mun_id_str[:2]
                        uf_map_cod = {
                            "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO",
                            "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA",
                            "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
                            "41": "PR", "42": "SC", "43": "RS",
                            "50": "MS", "51": "MT", "52": "GO", "53": "DF"
                        }
                        uf_sigla = uf_map_cod.get(codigo_uf)
                
                if not uf_sigla:
                    continue
                
                mun_id_7 = str(item.get("id", ""))
                if not mun_id_7:
                    continue
                mun_id_6 = mun_id_7[:6]
                mun_nome = item.get("nome", "Sem Nome")
                
                if uf_sigla not in municipios_por_uf:
                    municipios_por_uf[uf_sigla] = []
                municipios_por_uf[uf_sigla].append({
                    "id": mun_id_6,
                    "nome": mun_nome
                })
            
            # Ordena os municípios de cada UF alfabeticamente
            for uf in municipios_por_uf:
                municipios_por_uf[uf] = sorted(municipios_por_uf[uf], key=lambda x: x["nome"])
                
            ufs_ordenadas = sorted(list(municipios_por_uf.keys()))
            return ufs_ordenadas, municipios_por_uf
    except Exception as e:
        st.error(f"Erro ao obter lista de municípios do IBGE: {e}")
        
    return ["MA"], {"MA": [{"id": "210530", "nome": "Imperatriz"}]}

@st.cache_data(ttl=600, show_spinner=False)
def obter_toda_febre_amarela():
    """
    Baixa e faz cache de toda a base nacional de febre amarela (~3000 registros).
    Isso evita múltiplas paginações lentas nas trocas de cidades.
    """
    all_records = []
    limit = 1000
    offset = 0
    while True:
        url = f"{BASE_URL}/arboviroses/febre-amarela-humanos-primatas-nao-humanos"
        params = {"limit": limit, "offset": offset}
        r = requests.get(url, params=params, timeout=50)
        if r.status_code != 200:
            raise Exception(f"Erro HTTP {r.status_code} na consulta de febre amarela")
        items = r.json().get("febre_amarela_humanos_primatas", [])
        if not items:
            break
        all_records.extend(items)
        if len(items) < limit:
            break
        offset += limit
    return pd.DataFrame(all_records)

@st.cache_data(ttl=600, show_spinner=False)
def consultar_cnes_estabelecimentos(codigo_municipio):
    """Consulta os estabelecimentos do CNES diretamente do banco de dados PostgreSQL."""
    from src.database import criar_engine
    engine, _ = criar_engine()
    
    query = f"""
        SELECT 
            co_cnes as codigo_cnes,
            no_fantasia as nome_fantasia,
            no_razao_social as nome_razao_social,
            tp_unidade,
            co_tipo_unidade,
            nu_latitude as latitude_estabelecimento_decimo_grau,
            nu_longitude as longitude_estabelecimento_decimo_grau,
            no_bairro as bairro_estabelecimento,
            CASE 
                WHEN tp_gestao = 'E' THEN 'Estadual'
                WHEN tp_gestao = 'M' THEN 'Municipal'
                WHEN tp_gestao = 'F' THEN 'Federal'
                WHEN tp_gestao = 'D' THEN 'Dupla Gestão'
                ELSE 'Sem esfera definida'
            END as descricao_esfera_administrativa,
            CASE 
                WHEN co_turno_atendimento = '01' THEN 'DIURNO (MANHÃ OU TARDE)'
                WHEN co_turno_atendimento = '02' THEN 'DIURNO (MANHÃ E TARDE)'
                WHEN co_turno_atendimento = '03' THEN 'NOTURNO'
                WHEN co_turno_atendimento = '04' THEN 'DIURNO E NOTURNO'
                WHEN co_turno_atendimento = '05' THEN 'ATENDIMENTO COMERCIAL'
                WHEN co_turno_atendimento = '06' THEN 'ATENDIMENTO 24 HORAS'
                ELSE 'ATENDIMENTO EM HORÁRIO ESPECÍFICO'
            END as descricao_turno_atendimento,
            -- Deducao dos campos do painel
            CASE WHEN tp_unidade IN ('05', '07', '20', '21', '62') THEN 1 ELSE 0 END as estabelecimento_possui_atendimento_hospitalar,
            -- Centro cirúrgico: se for hospital geral/especializado ou pronto socorro, assume 1
            CASE WHEN tp_unidade IN ('05', '07', '20', '21') THEN 1 ELSE 0 END as estabelecimento_possui_centro_cirurgico,
            -- Centro obstétrico: se for hospital geral ou especializado (com indicação de obstetrícia/maternidade)
            CASE WHEN tp_unidade IN ('05', '07') AND (no_fantasia ILIKE '%maternidade%' OR no_fantasia ILIKE '%materno%' OR no_fantasia ILIKE '%obstetrico%' OR no_fantasia ILIKE '%obstetr%') THEN 1 
                 WHEN tp_unidade = '05' AND no_fantasia ILIKE '%hospital%' AND NOT (no_fantasia ILIKE '%olho%' OR no_fantasia ILIKE '%oftalmo%') THEN 1
                 ELSE 0 END as estabelecimento_possui_centro_obstetrico,
            -- Centro neonatal: se tiver indicação no nome
            CASE WHEN no_fantasia ILIKE '%neonatal%' OR no_fantasia ILIKE '%materno%' OR no_fantasia ILIKE '%infantil%' THEN 1 ELSE 0 END as estabelecimento_possui_centro_neonatal
        FROM tbestabelecimento
        WHERE co_municipio_gestor = '{codigo_municipio}'
    """
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn)
        return df
    except Exception as e:
        raise Exception(f"Erro ao consultar CNES no banco de dados: {e}")



@st.cache_data(ttl=600, show_spinner=False)
def consultar_arbovirose(disease_path, list_key, codigo_municipio, ano=None, mun_param="id_municip"):
    """Consulta dados de dengue, zika ou chikungunya para o município e ano."""
    url = f"{BASE_URL}/{disease_path}"
    params = {
        mun_param: codigo_municipio,
        "limit": 300
    }
    if ano:
        params["nu_ano"] = str(ano)
        
    r = requests.get(url, params=params, timeout=50)
    if r.status_code != 200:
        raise Exception(f"Erro HTTP {r.status_code} ao consultar {disease_path}")
    return pd.DataFrame(r.json().get(list_key, []))

def consultar_febre_amarela(codigo_municipio):
    """Filtra localmente a base nacional de febre amarela pelo código do município."""
    df_all = obter_toda_febre_amarela()
    if df_all.empty:
        return pd.DataFrame()
    
    # Filtra onde cod_mun_lpi bate com o município selecionado
    df_all["cod_mun_lpi_str"] = df_all["cod_mun_lpi"].astype(str).str.split(".").str[0].str.strip()
    df_filtered = df_all[df_all["cod_mun_lpi_str"] == str(codigo_municipio)].copy()
    return df_filtered

@st.cache_data(ttl=600, show_spinner=False)
def consultar_cnes_detalhado(codigo_municipio):
    """Consulta detalhada dos estabelecimentos do CNES com tipo de unidade e endereco."""
    from src.database import criar_engine
    from sqlalchemy import text
    engine, _ = criar_engine()

    query = f"""
        SELECT
            e.co_cnes as codigo_cnes,
            e.no_fantasia as nome_fantasia,
            e.no_razao_social as nome_razao_social,
            u.ds_tipo_unidade as descricao_tipo_unidade,
            e.tp_unidade as codigo_tipo_unidade,
            CASE
                WHEN e.tp_gestao = 'E' THEN 'Estadual'
                WHEN e.tp_gestao = 'M' THEN 'Municipal'
                WHEN e.tp_gestao = 'F' THEN 'Federal'
                WHEN e.tp_gestao = 'D' THEN 'Dupla Gestão'
                ELSE 'Sem esfera definida'
            END as descricao_esfera_administrativa,
            CASE
                WHEN e.co_turno_atendimento = '01' THEN 'DIURNO (MANHÃ OU TARDE)'
                WHEN e.co_turno_atendimento = '02' THEN 'DIURNO (MANHÃ E TARDE)'
                WHEN e.co_turno_atendimento = '03' THEN 'NOTURNO'
                WHEN e.co_turno_atendimento = '04' THEN 'DIURNO E NOTURNO'
                WHEN e.co_turno_atendimento = '05' THEN 'ATENDIMENTO COMERCIAL'
                WHEN e.co_turno_atendimento = '06' THEN 'ATENDIMENTO 24 HORAS'
                ELSE 'ATENDIMENTO EM HORÁRIO ESPECÍFICO'
            END as descricao_turno_atendimento,
            e.no_logradouro as logradouro,
            e.nu_endereco as numero_endereco,
            e.no_bairro as bairro_estabelecimento,
            e.co_cep as cep,
            e.nu_telefone as telefone,
            e.no_email as email,
            e.nu_latitude as latitude_estabelecimento_decimo_grau,
            e.nu_longitude as longitude_estabelecimento_decimo_grau,
            e.no_url as url,
            CASE WHEN e.st_conexao_internet = '1' THEN 'Sim' WHEN e.st_conexao_internet = '0' THEN 'Não' ELSE '' END as conexao_internet,
            CASE
                WHEN e.tp_unidade IN ('05', '07', '20', '21', '62') THEN 1 ELSE 0
            END as estabelecimento_possui_atendimento_hospitalar,
            CASE WHEN e.tp_unidade IN ('05', '07', '20', '21') THEN 1 ELSE 0
            END as estabelecimento_possui_centro_cirurgico
        FROM tbestabelecimento e
        LEFT JOIN tbtipounidade u ON u.co_tipo_unidade::text = e.tp_unidade::text
        WHERE e.co_municipio_gestor = '{codigo_municipio}'
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn)
        return df
    except Exception as e:
        raise Exception(f"Erro ao consultar CNES detalhado no banco de dados: {e}")


@st.cache_data(ttl=600, show_spinner=False)
def consultar_cnes_leitos(codigo_municipio):
    """Consulta leitos hospitalares por estabelecimento a partir do CNES."""
    from src.database import criar_engine
    from sqlalchemy import text
    engine, _ = criar_engine()

    query = f"""
        SELECT
            e.co_cnes as codigo_cnes,
            e.no_fantasia as nome_fantasia,
            c.co_tipo_leito::numeric as codigo_tipo_leito,
            CASE c.co_tipo_leito::numeric
                WHEN 1 THEN 'Cirúrgico'
                WHEN 2 THEN 'Clínico'
                WHEN 3 THEN 'Complementar (UTI/Intermediário)'
                WHEN 4 THEN 'Obstétrico'
                WHEN 5 THEN 'Pediátrico'
                WHEN 6 THEN 'Crônico (Psiquiatria/Reabilitação)'
                WHEN 7 THEN 'Hospital Dia'
                ELSE 'Outros'
            END as descricao_tipo_leito,
            COALESCE(c.qt_exist::numeric, 0)::int as leitos_existentes,
            COALESCE(c.qt_contr::numeric, 0)::int as leitos_contratados,
            COALESCE(c.qt_sus::numeric, 0)::int as leitos_sus
        FROM rlestabcomplementar c
        JOIN tbestabelecimento e ON e.co_unidade = c.co_unidade
        WHERE e.co_municipio_gestor = '{codigo_municipio}'
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn)
        return df
    except Exception as e:
        raise Exception(f"Erro ao consultar leitos do CNES no banco de dados: {e}")


@st.cache_data(ttl=600, show_spinner=False)
def consultar_cnes_subtipos(codigo_municipio):
    """Consulta subtipos de unidades (CAPS, UPA, laboratórios, CASAI, CER, etc.)."""
    from src.database import criar_engine
    from sqlalchemy import text
    engine, _ = criar_engine()

    query = f"""
        SELECT
            e.co_cnes as codigo_cnes,
            e.no_fantasia as nome_fantasia,
            u.ds_tipo_unidade as descricao_tipo_unidade,
            st.ds_sub_tipo as descricao_subtipo
        FROM rlestabsubtipo r
        JOIN tbestabelecimento e ON e.co_unidade = r.co_unidade
        LEFT JOIN tbtipounidade u ON u.co_tipo_unidade::text = e.tp_unidade::text
        LEFT JOIN tbsubtipo st
            ON st.co_tipo_unidade::text = r.co_tipo_unidade::text
            AND st.co_sub_tipo::text = r.co_sub_tipo_unidade::text
        WHERE e.co_municipio_gestor = '{codigo_municipio}'
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn)
        return df
    except Exception as e:
        raise Exception(f"Erro ao consultar subtipos do CNES no banco de dados: {e}")


@st.cache_data(ttl=600, show_spinner=False)
def consultar_cnes_samu_regulacao(codigo_municipio):
    """Consulta veículos do SAMU e centrais de regulação de urgências."""
    from src.database import criar_engine
    from sqlalchemy import text
    engine, _ = criar_engine()

    query_veiculos = f"""
        SELECT
            e.co_cnes as codigo_cnes,
            e.no_fantasia as nome_fantasia,
            r.co_placa as placa,
            r.nu_chassi as chassi,
            r.dt_ativacao as data_ativacao,
            r.dt_desativacao as data_desativacao
        FROM rlestabsamu r
        JOIN tbestabelecimento e ON e.co_unidade = r.co_unidade
        WHERE e.co_municipio_gestor = '{codigo_municipio}'
    """
    query_centrais = f"""
        SELECT
            e.co_cnes as codigo_cnes,
            e.no_fantasia as nome_fantasia,
            r.no_central as nome_central,
            r.no_bairro as bairro
        FROM rlestabcentralreg r
        JOIN tbestabelecimento e ON e.co_unidade = r.co_unidade
        WHERE e.co_municipio_gestor = '{codigo_municipio}'
    """
    try:
        with engine.connect() as conn:
            df_veiculos = pd.read_sql_query(text(query_veiculos), conn)
            df_centrais = pd.read_sql_query(text(query_centrais), conn)
        return df_veiculos, df_centrais
    except Exception as e:
        raise Exception(f"Erro ao consultar SAMU/Regulação do CNES: {e}")


@st.cache_data(ttl=600, show_spinner=False)
def consultar_cnes_servicos(codigo_municipio):
    """Consulta serviços referenciados (SADT, oncologia, etc.) por estabelecimento."""
    from src.database import criar_engine
    from sqlalchemy import text
    engine, _ = criar_engine()

    query = f"""
        SELECT
            e.co_cnes as codigo_cnes,
            e.no_fantasia as nome_fantasia,
            t.ds_tipo_servico_referenciado as descricao_servico,
            sr.no_razao_social as razao_social_prestador
        FROM tbservicoreferenciado sr
        JOIN tbestabelecimento e ON e.co_unidade = sr.co_unidade
        LEFT JOIN tbtiposervicoreferenciado t
            ON t.tp_tipo_servico_referenciado::text = sr.tp_servico_referenciado::text
        WHERE e.co_municipio_gestor = '{codigo_municipio}'
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn)
        return df
    except Exception as e:
        raise Exception(f"Erro ao consultar serviços referenciados do CNES: {e}")


@st.cache_data(ttl=600, show_spinner=False)
def consultar_previne_brasil(codigo_municipio):
    """Consulta indicadores de desempenho do Previne Brasil para o município."""
    url = f"{BASE_URL}/atencao-primaria/indicador-desempenho-programa-previne-brasil"
    params = {"codigo_municipio": codigo_municipio, "limit": 100}
    r = requests.get(url, params=params, timeout=50)
    if r.status_code != 200:
        raise Exception(f"Erro HTTP {r.status_code} ao consultar Previne Brasil")
    return pd.DataFrame(r.json().get("sisab_indicador_desempenho", []))

@st.cache_data(ttl=600, show_spinner=False)
def consultar_sisagua(codigo_municipio):
    """Consulta parâmetros básicos de vigilância da qualidade da água (SISAGUA)."""
    url = f"{BASE_URL}/sisagua/vigilancia-parametros-basicos"
    params = {"codigo_ibge": codigo_municipio, "limit": 200}
    r = requests.get(url, params=params, timeout=50)
    if r.status_code != 200:
        raise Exception(f"Erro HTTP {r.status_code} ao consultar SISAGUA")
    return pd.DataFrame(r.json().get("parametros", []))

@st.cache_data(ttl=600, show_spinner=False)
def consultar_sisvan(codigo_municipio):
    """Consulta informações de acompanhamento de estado nutricional (SISVAN)."""
    url = f"{BASE_URL}/sisvan/estado-nutricional"
    params = {"codigo_municipio": codigo_municipio, "limit": 200}
    r = requests.get(url, params=params, timeout=50)
    if r.status_code != 200:
        raise Exception(f"Erro HTTP {r.status_code} ao consultar SISVAN")
    return pd.DataFrame(r.json().get("estados_nutricionais", []))
