
from case_style import snake_keys_to_camel
from database import execute_query, sql_replace_params, execute_query_to_dataframe
from fastapi import HTTPException
from .layer import prepare_layer_info
from .query import *
import os
import pandas as pd


PG_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format( os.environ['DB_USER'],
                                                    os.environ['DB_PASSWORD'],
                                                    os.environ['DB_HOST'],
                                                    os.environ['DB_PORT'],
                                                    os.environ['DB_NAME'])
MES_DICT = {
  1: 'Janeiro',
  2: 'Fevereiro',
  3: 'Março',
  4: 'Abril',
  5: 'Maio',
  6: 'Junho',
  7: 'Julho',
  8: 'Agosto',
  9: 'Setembro',
  10: 'Outubro',
  11: 'Novembro',
  12: 'Dezembro'}

ESTADOS_DICT = {
"AC": {"nome": "Acre", "prefixo": "do"},
"AP": {"nome": "Amapá", "prefixo": "do"},
"AM": {"nome": "Amazonas", "prefixo": "do"},
"MT": {"nome": "Mato Grosso ", "prefixo": "do"},
"PA": {"nome": "Pará", "prefixo": "do"},
"RO": {"nome": "Rondônia", "prefixo": "de"},
"RR": {"nome": "Roraima", "prefixo": "de"},
}

def get_entenda_data(esfera=None, ufs=None, fpnd=None):
    params = { 'where_clause': _generate_where_clause(esfera, ufs, fpnd)}
    informacao_df = execute_query_to_dataframe(PG_URI, sql_replace_params(DQ_ENTENDA_INFORMACAO, params)) 
    desmatamento_df = execute_query_to_dataframe(PG_URI, sql_replace_params(DQ_ENTENDA_DESMATAMENTO, params))  

    fpnd_area_total_ha = informacao_df['fpnd_area_ha'].sum()
    if fpnd_area_total_ha == 0:
        return _get_empty_result(ufs)
    
    result = {
        **_get_entenda_s_biodiversidade(informacao_df, esfera),
        **_get_entenda_s_car(informacao_df, fpnd_area_total_ha),
        **_get_entenda_s_carbono(informacao_df),
        **_get_entenda_s_categoria(informacao_df, fpnd_area_total_ha),
        **_get_entenda_s_desmatamento(informacao_df),
        **_get_entenda_s_entenda(informacao_df, fpnd_area_total_ha),
        **_get_entenda_s_mineracao(informacao_df),
        **_get_info_deter(desmatamento_df),
        **_get_info_prodes(desmatamento_df),
        **_get_territorial_context(ufs),
        }

    return snake_keys_to_camel(result)

def get_fpnd_as_mvt(z,x,y):
    params = {
        'z': z,
        'x': x,
        'y': y
    }
    query = sql_replace_params(DQ_GEO_FPND_AS_MVT, params)
    return execute_query(PG_URI, query)[0]['mvt'].tobytes()

def get_map_data():
    try:
        last_month = execute_query(PG_URI, DQ_MAP_DATA_LAST_MONTH)[0]['month']

        responses = _get_layers(last_month)

        layers_legends = {}
        layers_data = []
        for lyr in responses:
            layers_legends[lyr['layer_name']] = lyr['legend']
            layers_data.append(lyr['data'])
        data = pd.concat(layers_data, axis=1, ignore_index=False)
        
        return snake_keys_to_camel({
            'last_month': last_month,
            'layers_legends':layers_legends,
            'data': data.T.to_dict('dict')
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _generate_where_clause(esfera=None, ufs=None, fpnd=None):
    conditions = []
    
    if esfera:
        conditions.append(f"esfera = '{esfera}'")
    
    if ufs:
        states_str = ', '.join(f"'{state}'" for state in ufs)
        conditions.append(f"uf IN ({states_str})")
    
    if fpnd:
        conditions.append(f"codigo = '{fpnd}'")
    
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
    else:
        where_clause = ""
    
    return where_clause

def _get_deforestation_last_month(last_month, offset=25):
    df = execute_query_to_dataframe(PG_URI, DQ_MAP_DATA_DEFORESTATION_LAST_MONTH)       
    result = prepare_layer_info(
            df, 
            'deforastation_last_month',
            f'Desmatamento no último mês de {last_month} em ha' )
    df = result['data']

    gray = '#80808000'  # Hexadecimal for gray
    if gray not in df['deforastation_last_month_color'].cat.categories:
        df['deforastation_last_month_color'] = df['deforastation_last_month_color'].cat.add_categories([gray])

    df.iloc[offset:, df.columns.get_loc('deforastation_last_month_color')] = gray
    result['data'] = df
    return result
 
def _get_deforestation_last_ten_years():
    df = execute_query_to_dataframe(PG_URI, DQ_MAP_DATA_DEFORESTATION_LAST_10_YEARS)       
    return prepare_layer_info(
            df, 
            'deforastation_last_10_years',
            f'Desmatamento dos últimos 10 anos em ha' )
     
def _get_entenda_s_biodiversidade(informacao_df, esfera):
    return {
        # Média da diversidade de espécies nas FPND categorizadas como "Federal" e arredondando o resultado para duas casas decimais
        'biodiversidade_fpnd_federal_media': round(informacao_df[informacao_df['esfera'] == 'Federal']['especie_diversidade_media'].mean(), 2) if esfera in [None, 'Federal'] else 0,
        # Média da diversidade de espécies nas FPND categorizadas como "Federal" e arredondando o resultado para duas casas decimais
        'biodiversidade_fpnd_todas_media': round(informacao_df['especie_diversidade_media'].mean(), 2)
    }

def _get_entenda_s_car(informacao_df, fpnd_area_total_ha):
    result = {}

    # Calculando a área total de sobreposição do CAR com as FPND em hectares e arredondando o resultado para duas casas decimais
    car_sobreposicao_fpnd_area_ha = round(informacao_df['car_sobreposicao_fpnd_ha'].sum(), 2)
    result['car_sobreposicao_fpnd_area_ha'] = car_sobreposicao_fpnd_area_ha

    # Calculando a equivalência da área de sobreposição do CAR com FPND em quantidade de campos de futebol
    result['car_sobreposicao_fpnd_equivalencia_futebol_qtd'] = round(informacao_df['car_sobreposicao_fpnd_ha'].sum() / 0.714, 2)

    # Calculando a porcentagem da área de sobreposição do CAR com FPND em relação à área total das FPND e arredondando o resultado para duas casas decimais
    # Certifique-se de que o denominador não é zero para evitar divisão por zero
    result['car_sobreposicao_fpnd_area_per'] = str(round((informacao_df['car_sobreposicao_fpnd_ha'].sum() / fpnd_area_total_ha) * 100, 2))

    # Calculate the mean deforestation area for both groups
    car = informacao_df['car_sobreposicao_fpnd_ha'].sum()
    desmatamento = informacao_df['desmatamento_area_ha'].sum()
    if desmatamento > 0:
        result['car_comparacao_desmatamento'] = int(car/desmatamento)
    else:
        result['car_comparacao_desmatamento'] = 0

    result['car_grafico'] = [
        {'xField': 'Total', 'colorField': 'CAR', 'yField': round(car_sobreposicao_fpnd_area_ha, 1)},
        {'xField': 'Total', 'colorField': 'FPND', 'yField': round(fpnd_area_total_ha-car_sobreposicao_fpnd_area_ha, 1)},
    ]
    return result

def _get_entenda_s_carbono(informacao_df):
    carbono_estoque_ton = informacao_df['carbono_estoque_ton'].sum()
    return {
        # Calculando o estoque total de carbono no solo em toneladas e arredondando o resultado para duas casas decimais
        'estoque_carbono_ton': round(carbono_estoque_ton, 2,),
        # Calculando a equivalência total do estoque de carbono em peso de CO2 em toneladas e arredondando o resultado para duas casas decimais
        'estoque_carbono_equivalencia_peso_ton':round(carbono_estoque_ton * 3.17, 2)
    }

def _get_entenda_s_categoria(informacao_df, fpnd_area_total_ha):
    return {
        # Calculando a área total das FPND categorizadas como "Estadual" e arredondando o resultado para duas casas decimais
        'categoria_fpnd_estadual_area_per':  str(round((informacao_df[informacao_df['esfera'] == 'Estadual']['fpnd_area_ha'].sum() / fpnd_area_total_ha) * 100 , 2)),
        # Calculando a área total das FPND categorizadas como "Federal" e arredondando o resultado para duas casas decimais
        'categoria_fpnd_federal_area_per': str(round((informacao_df[informacao_df['esfera'] == 'Federal']['fpnd_area_ha'].sum() / fpnd_area_total_ha) * 100, 2))
    }

def _get_entenda_s_desmatamento(informacao_df):
    result = {}

    # Área de desmatamento Total nas FPNDs
    result['desmatamento_area_ha'] = round(informacao_df['desmatamento_area_ha'].sum(), 2)

    # Área de florestas nativas nas FPNDs
    result['desmatamento_floresta_nativa_ha'] = round(informacao_df['floresta_atual_area_ha'].sum(), 2) 
    # Gráfico

    floresta = informacao_df[informacao_df['esfera'] == 'Estadual']['floresta_atual_area_ha'].sum()
    desmatamento = informacao_df[informacao_df['esfera'] == 'Estadual']['desmatamento_area_ha'].sum()
    total = floresta+desmatamento
    if total == 0:
        result['desmatamento_grafico_fpnd_estaduais'] = None
    else:
        result['desmatamento_grafico_fpnd_estaduais'] = [
            {'colorField': 'Floresta', 'angleField': round((floresta/total)*100,1) },
            {'colorField': 'Desmatamento', 'angleField': round((desmatamento/total)*100,1)}
        ]
    return result

def _get_entenda_s_entenda(informacao_df, fpnd_area_total_ha):
    return {
        # Calculando a área total da floresta pública não destinada (fpnd_area_ha) e arredondando o resultado para duas casas decimais
        'entenda_fpnd_area_total_ha': round(informacao_df['fpnd_area_ha'].sum(),2),
        # Calculando a quantidade equivalente de campos de futebol para a área total das FPND (fpnd_area_ha)
        # Considerando que cada campo de futebol possui aproximadamente 0.714 hectares
        'entenda_fpnd_equivalencia_futebol_qtd': round(fpnd_area_total_ha / 0.714, 2)
    }

def _get_entenda_s_mineracao(informacao_df):
    return {
        # Calculando a área total de interseção de mineração com as FPND em hectares e arredondando o resultado para duas casas decimais
        'mineracao_sobreposicao_fpnd_area_ha': round(informacao_df['mineracao_area_ha'].sum(), 2),
        # Calculando a equivalência da área de interseção de mineração com FPND em quantidade de campos de futebol
        'mineracao_sobreposicao_fpnd_equivalencia_futebol_qtd': round(informacao_df['mineracao_area_ha'].sum() / 0.714, 2)
    }

def _get_info_deter(desmatamento_df):

    # Convertendo a coluna 'data' para datetime
    desmatamento_df['data'] = pd.to_datetime(desmatamento_df['data'])

    # Filtrando o DataFrame para entradas onde a fonte é 'DETER'
    deter_df = desmatamento_df[desmatamento_df['fonte'] == 'deter'].reset_index()

    # Encontrando o último mês disponível no DataFrame para dados 'DETER'
    ultimo_mes = deter_df['data'].dt.to_period('M').max()
    dados_ultimo_mes = deter_df[deter_df['data'].dt.to_period('M') == ultimo_mes]

    # Calculando o total de área desmatada no último mês
    alerta_mensal_desmatamento_ultimo_mes_ha = dados_ultimo_mes['area_ha'].sum()

    # Comparando com o mesmo mês do ano anterior
    mes_ano_anterior = ultimo_mes - 12
    dados_ano_anterior = deter_df[deter_df['data'].dt.to_period('M') == mes_ano_anterior]
    area_ano_anterior = dados_ano_anterior['area_ha'].sum() if not dados_ano_anterior.empty else 0

    # Calculando a diferença percentual
    if area_ano_anterior > 0:
        value = round(abs(((alerta_mensal_desmatamento_ultimo_mes_ha - area_ano_anterior) / area_ano_anterior) * 100), 2)
        alerta_mensal_desmatamento_comparacao_mesmo_mes_ano_anterio_perultimo_mes_per = \
            str(value)
        alerta_mensal_desmatamento_comparacao_mesmo_mes_ano_anterio_direcao = 'maior' if value > 0 else 'menor'
    else:
        alerta_mensal_desmatamento_comparacao_mesmo_mes_ano_anterio_perultimo_mes_per = ''
        alerta_mensal_desmatamento_comparacao_mesmo_mes_ano_anterio_direcao = ''

    if ultimo_mes.month == pd.notna:
        ultimo_mes_nome = MES_DICT[ultimo_mes.month]
    else:
        ultimo_mes_nome = ''

    deter_df = pd.DataFrame({
        'ano': deter_df['data'].dt.year,   # Extraindo o ano da coluna 'data'
        'mes': deter_df['data'].dt.month,  # Extraindo o mês da coluna 'data'
        'area_ha': deter_df['area_ha']     # Mantendo a coluna 'area_ha'
    })

    # Agrupando por ano e mês e somando a área desmatada
    grouped_df = deter_df.groupby(['ano', 'mes']).agg(y_field=('area_ha', 'sum')).round(1)
    # Resetar o índice para transformar 'ano' e 'mes' em colunas
    grouped_df.reset_index(inplace=True)

    # Substituir os valores de 'mes' pelos nomes usando o dicionário MES_DICT
    grouped_df['mes'] = grouped_df['mes'].map({ k:v[:3] for k, v in MES_DICT.items()})
    grouped_df['ano'] = grouped_df['ano'].astype(str)
    grouped_df.rename(columns={'ano':'colorField', 'mes': 'xField'}, inplace=True)
    alerta_mensal_grafico_historico_desmatamento = grouped_df.to_dict(orient='records')

    return {
        'ultimo_mes': ultimo_mes_nome,
        'alerta_mensal_desmatamento_ultimo_mes_ha': round(alerta_mensal_desmatamento_ultimo_mes_ha, 2),
        'alerta_mensal_desmatamento_comparacao_mesmo_mes_ano_anterio_per': alerta_mensal_desmatamento_comparacao_mesmo_mes_ano_anterio_perultimo_mes_per,
        'alerta_mensal_desmatamento_comparacao_mesmo_mes_ano_anterio_direcao': alerta_mensal_desmatamento_comparacao_mesmo_mes_ano_anterio_direcao,
        'alerta_mensal_grafico_historico_desmatamento': alerta_mensal_grafico_historico_desmatamento
        }

def _get_info_prodes(desmatamento_df):

    # Convertendo a coluna 'data' para datetime
    desmatamento_df['data'] = pd.to_datetime(desmatamento_df['data'])

    # Filtrando o DataFrame para entradas onde a fonte é 'PRODES'
    prodes_df = desmatamento_df[desmatamento_df['fonte'] == 'prodes'].reset_index()

    # Encontrando o primeiro e o último ano disponível no DataFrame para dados 'PRODES'
    primeiro_ano = prodes_df['data'].dt.to_period('Y').min()
    ultimo_ano = prodes_df['data'].dt.to_period('Y').max()

    
    dados_primeiro_ano = prodes_df[prodes_df['data'].dt.to_period('Y') == primeiro_ano]
    dados_ultimo_ano = prodes_df[prodes_df['data'].dt.to_period('Y') == ultimo_ano]

    # Calculando o total de área desmatada 
    desmatamento_primeiro_ano_ha = dados_primeiro_ano['area_ha'].sum()
    desmatamento_ultimo_ano_ha = dados_ultimo_ano['area_ha'].sum()


    # Calculando a diferença percentual
    if desmatamento_primeiro_ano_ha > 0:
        desmatamento_comparacao_primeiro_ano_ultimo_ano_per = \
            str(round(((desmatamento_ultimo_ano_ha - desmatamento_primeiro_ano_ha) / desmatamento_primeiro_ano_ha) * 100, 2))
    else:
        desmatamento_comparacao_primeiro_ano_ultimo_ano_per = ''

    prodes_df = pd.DataFrame({
        'ano': prodes_df['data'].dt.year,   # Extraindo o ano da coluna 'data'
        'area_ha': prodes_df['area_ha']     # Mantendo a coluna 'area_ha'
    })

    # Agrupando por ano e somando a área desmatada
    grouped_df = prodes_df.groupby(['ano']).agg(y_field=('area_ha', 'sum')).round(1)
    # Resetar o índice para transformar 'ano' em coluna
    grouped_df.reset_index(inplace=True)
    grouped_df['y_field'] = grouped_df['y_field'].cumsum()
    grouped_df.rename(columns={'ano': 'xField'}, inplace=True)
    desmatamento_grafico_desmatamento_acumulado = grouped_df.to_dict(orient='records')

    return {
        'primeiro_ano': str(primeiro_ano.year),
        'ultimo_ano': str(ultimo_ano.year),
        'desmatamento_comparacao_primeiro_ano_ultimo_ano_per': desmatamento_comparacao_primeiro_ano_ultimo_ano_per,
        'desmatamento_grafico_desmatamento_acumulado': desmatamento_grafico_desmatamento_acumulado
        }

def _get_layers(last_month):
    layers = [
            { 'value_name': 'land_cover', 'legend_title': 'Área desmatada até 2022 em ha'},
            { 'value_name': 'underground_carbon_storage', 'legend_title': 'Densidade de Carbono em ton/ha'},
            { 'value_name': 'species_diversity', 'legend_title': 'Média de  diversidade de espécies'},
            { 'value_name': 'car_overlap', 'legend_title': 'Percentual de área FPND sobreposta com área de CAR'},
            { 'value_name': 'mining', 'legend_title': 'Área de Mineração em FPND em ha'}]
    result = [
        _get_deforestation_last_month(last_month),
        _get_deforestation_last_ten_years()
    ]

    df = execute_query_to_dataframe(PG_URI, DQ_MAP_DATA)  
    for lyr in layers:
        result.append(prepare_layer_info(
            df, 
            lyr['value_name'],
            lyr['legend_title']))
    return result

def _get_territorial_context(ufs):
    recorte_prefixo =  'o bioma'
    recorte_nome = 'Amazônico'

    if ufs and len(ufs) == 1:
        recorte_prefixo =  f'o estado {ESTADOS_DICT[ufs[0]]['prefixo']}'
        recorte_nome = ESTADOS_DICT[ufs[0]]['nome']
    if ufs and len(ufs) > 1:
        ufs.sort()
        recorte_prefixo =  f'os estados {ESTADOS_DICT[ufs[0]]['prefixo']}'
        recorte_nome = ', '.join([ ESTADOS_DICT[uf]['nome'] for uf in ufs[:-1]]) + f' e {ESTADOS_DICT[ufs[-1]]['nome']}'
 
    return {
        'recorte_prefixo': recorte_prefixo,
        'recorte_nome': recorte_nome
    }


def _get_empty_result(ufs):
    result =  {
            "biodiversidade_fpnd_federal_media": 0,
            "biodiversidade_fpnd_todas_media": 0,
            "car_sobreposicao_fpnd_area_ha": 0,
            "car_sobreposicao_fpnd_equivalencia_futebol_qtd": 0,
            "car_sobreposicao_fpnd_area_per": "0.0",
            "car_comparacao_desmatamento": 0,
            "car_grafico": [
                {
                "xField": "Total",
                "colorField": "CAR",
                "yField": 0
                },
                {
                "xField": "Total",
                "colorField": "FPND",
                "yField": 0
                }
            ],
            "estoque_carbono_ton": 0,
            "estoque_carbono_equivalencia_peso_ton": 0,
            "categoria_fpnd_estadual_area_per": "0.0",
            "categoria_fpnd_federal_area_per": "0.0",
            "desmatamento_area_ha": 0,
            "desmatamento_floresta_nativa_ha": 0,
            "desmatamento_grafico_fpnd_estaduais": [
                {
                "colorField": "Floresta",
                "angleField": 0
                },
                {
                "colorField": "Desmatamento",
                "angleField": 0
                }
            ],
            "entenda_fpnd_area_total_ha": 0,
            "entenda_fpnd_equivalencia_futebol_qtd": 0,
            "mineracao_sobreposicao_fpnd_area_ha": 0,
            "mineracao_sobreposicao_fpnd_equivalencia_futebol_qtd": 0,
            "ultimo_mes": "",
            "alerta_mensal_desmatamento_ultimo_mes_ha": 0,
            "alerta_mensal_desmatamento_comparacao_mesmo_mes_ano_anterio_per": "0.0",
            "alerta_mensal_desmatamento_comparacao_mesmo_mes_ano_anterio_direcao": "",
            "alerta_mensal_grafico_historico_desmatamento": [
                {
                "colorField": "2023",
                "xField": "Jan",
                "y_field": 0
                },
                {
                "colorField": "2023",
                "xField": "Fev",
                "y_field": 0
                },
                {
                "colorField": "2023",
                "xField": "Mar",
                "y_field": 0
                },
                {
                "colorField": "2023",
                "xField": "Abr",
                "y_field": 0
                },
                {
                "colorField": "2023",
                "xField": "Mai",
                "y_field": 0
                },
                {
                "colorField": "2023",
                "xField": "Jun",
                "y_field": 0
                },
                {
                "colorField": "2023",
                "xField": "Jul",
                "y_field": 0
                },
                {
                "colorField": "2023",
                "xField": "Ago",
                "y_field": 0
                },
                {
                "colorField": "2023",
                "xField": "Set",
                "y_field": 0
                },
                {
                "colorField": "2023",
                "xField": "Out",
                "y_field": 0
                },
                {
                "colorField": "2023",
                "xField": "Nov",
                "y_field": 0
                },
                {
                "colorField": "2023",
                "xField": "Dez",
                "y_field": 0
                }, {
                "colorField": "2024",
                "xField": "Jan",
                "y_field": 0
                },
                {
                "colorField": "2024",
                "xField": "Fev",
                "y_field": 0
                },
                {
                "colorField": "2024",
                "xField": "Mar",
                "y_field": 0
                },
                {
                "colorField": "2024",
                "xField": "Abr",
                "y_field": 0
                },
                {
                "colorField": "2024",
                "xField": "Mai",
                "y_field": 0
                },
                {
                "colorField": "2024",
                "xField": "Jun",
                "y_field": 0
                },
                {
                "colorField": "2024",
                "xField": "Jul",
                "y_field": 0
                },
                {
                "colorField": "2024",
                "xField": "Ago",
                "y_field": 0
                },
                {
                "colorField": "2024",
                "xField": "Set",
                "y_field": 0
                },
                {
                "colorField": "2024",
                "xField": "Out",
                "y_field": 0
                },
                {
                "colorField": "2024",
                "xField": "Nov",
                "y_field": 0
                },
                {
                "colorField": "2024",
                "xField": "Dez",
                "y_field": 0
                }            
            ],
            "primeiro_ano": "2013",
            "ultimo_ano": "2023",
            "desmatamento_comparacao_primeiro_ano_ultimo_ano_per": "",
            "desmatamento_grafico_desmatamento_acumulado": [
                {
                "xField": 2013,
                "y_field": 0
                },
                {
                "xField": 2014,
                "y_field": 0
                },
                {
                "xField": 2015,
                "y_field": 0
                },
                {
                "xField": 2016,
                "y_field": 0
                },
                {
                "xField": 2017,
                "y_field": 0
                },
                {
                "xField": 2018,
                "y_field": 0
                },
                {
                "xField": 2019,
                "y_field": 0
                },
                {
                "xField": 2020,
                "y_field": 0
                },
                {
                "xField": 2021,
                "y_field": 0
                },
                {
                "xField": 2022,
                "y_field": 0
                },
                {
                "xField": 2023,
                "y_field": 0
                }
            ],
            **_get_territorial_context(ufs)}
    return snake_keys_to_camel(result)

    