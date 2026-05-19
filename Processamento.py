##################################################################
################### PROCESSAMENTO OPERACIONAL ####################
###################### BLUEOCEAN METEO ###########################
##################################################################

import openmeteo_requests
import requests_cache
import pandas as pd
import numpy as np

from retry_requests import retry
from datetime import datetime

##################################################################
######################## CONFIGURAÇÕES ############################
##################################################################

ARQUIVO_ESTACOES = r"C:\Users\mario\Documents\BLUEOCEAN\TRABALHO\LAT E LON ESTAÇÕES PBR.xlsx"

FORECAST_DAYS = 3

##################################################################
######################## MODELOS #################################
##################################################################

MODELOS = [

    "ecmwf_ifs",
    "gfs_global",
    "icon_global",
    "ukmo_global_deterministic_10km",
    "meteofrance_arpege_world"
]

##################################################################
######################## OPEN-METEO ##############################
##################################################################

cache_session = requests_cache.CachedSession(
    '.cache',
    expire_after=3600
)

retry_session = retry(
    cache_session,
    retries=5,
    backoff_factor=0.2
)

openmeteo = openmeteo_requests.Client(
    session=retry_session
)

##################################################################
######################## LEITURA #################################
##################################################################

df_estacoes = pd.read_excel(
    ARQUIVO_ESTACOES
)

df_estacoes["Estação"] = (

    df_estacoes["Estação"]
    .astype(str)
    .str.strip()
)

##################################################################
######################## FUNÇÕES #################################
##################################################################

def classificar_chuva(valor):

    if valor < 1:
        return "Sem chuva"

    elif valor < 10:
        return "Chuva fraca"

    elif valor <= 25:
        return "Chuva moderada"

    else:
        return "Chuva forte"

# ================================================================

def direcao_cardinal(graus):

    direcoes = [

        "N",
        "NE",
        "E",
        "SE",
        "S",
        "SO",
        "O",
        "NO"
    ]

    idx = round(graus / 45) % 8

    return direcoes[idx]

# ================================================================

def calcular_prob_raios(
    cape,
    prob_chuva,
    rajada
):

    valor = (

        (cape / 3000) * 40 +
        (prob_chuva * 0.4) +
        (rajada * 0.5)
    )

    return int(
        min(100, max(0, valor))
    )

# ================================================================

def classificar_risco(
    prob_raios,
    rajada,
    chuva
):

    if prob_raios >= 70 or rajada >= 50:
        return "Vermelho"

    elif prob_raios >= 30 or chuva >= 10:
        return "Amarelo"

    else:
        return "Verde"

##################################################################
######################## UV ######################################
##################################################################

def classificar_uv(valor):

    if valor <= 2:
        return "Baixo"

    elif valor <= 5:
        return "Moderado"

    elif valor <= 7:
        return "Alto"

    elif valor <= 10:
        return "Muito Alto"

    else:
        return "Extremo"

# ================================================================

def cor_uv(valor):

    if valor <= 5:
        return "Verde"

    elif valor <= 7:
        return "Amarelo"

    else:
        return "Vermelho"

##################################################################
######################## RESULTADOS ##############################
##################################################################

lista_resultados = []

##################################################################
######################## LOOP ESTAÇÕES ###########################
##################################################################

for _, linha in df_estacoes.iterrows():

    try:

        estacao = linha["Estação"]

        lat = float(
            linha["Lat"]
        )

        lon = float(
            linha["Lon"]
        )

        print(
            f"Processando: {estacao}"
        )

        ##########################################################
        ###################### API ###############################
        ##########################################################

        url = "https://api.open-meteo.com/v1/forecast"

        params = {

            "latitude": lat,
            "longitude": lon,

            "hourly": [

                "temperature_2m",
                "relative_humidity_2m",

                "wind_speed_10m",
                "wind_gusts_10m",
                "wind_direction_10m",

                "precipitation_probability",
                "precipitation",

                "uv_index",

                "cape"
            ],

            "models": MODELOS,

            "forecast_days": FORECAST_DAYS,

            "timezone": "America/Fortaleza"
        }

        responses = openmeteo.weather_api(
            url,
            params=params
        )

        ##########################################################
        ###################### ENSEMBLE ##########################
        ##########################################################

        lista_modelos = []

        for response in responses:

            hourly = response.Hourly()

            dados = pd.DataFrame({

                "date": pd.date_range(

                    start=pd.to_datetime(
                        hourly.Time(),
                        unit="s"
                    ),

                    end=pd.to_datetime(
                        hourly.TimeEnd(),
                        unit="s"
                    ),

                    freq=pd.Timedelta(
                        seconds=hourly.Interval()
                    ),

                    inclusive="left"
                ),

                "temperature":
                    hourly.Variables(0).ValuesAsNumpy(),

                "humidity":
                    hourly.Variables(1).ValuesAsNumpy(),

                "wind_speed":
                    hourly.Variables(2).ValuesAsNumpy(),

                "wind_gusts":
                    hourly.Variables(3).ValuesAsNumpy(),

                "wind_direction":
                    hourly.Variables(4).ValuesAsNumpy(),

                "rain_probability":
                    hourly.Variables(5).ValuesAsNumpy(),

                "precipitation":
                    hourly.Variables(6).ValuesAsNumpy(),

                "uv":
                    hourly.Variables(7).ValuesAsNumpy(),

                "cape":
                    hourly.Variables(8).ValuesAsNumpy(),
            })

            lista_modelos.append(dados)

        ##########################################################
        ###################### MÉDIA #############################
        ##########################################################

        df_media = lista_modelos[0].copy()

        variaveis = [

            "temperature",
            "humidity",

            "wind_speed",
            "wind_gusts",
            "wind_direction",

            "rain_probability",
            "precipitation",

            "uv",

            "cape"
        ]

        for var in variaveis:

            df_media[var] = np.nanmean(

                [
                    df[var]
                    for df in lista_modelos
                ],

                axis=0
            )

        ##########################################################
        ###################### DIAS ##############################
        ##########################################################

        df_media["dia"] = (
            df_media["date"].dt.date
        )

        dias = sorted(
            df_media["dia"].unique()
        )

        ##########################################################
        ###################### RESUMO ############################
        ##########################################################

        for dia in dias:

            df_dia = df_media[
                df_media["dia"] == dia
            ]

            ######################################################
            ################## VARIÁVEIS #########################
            ######################################################

            tmin = round(
                np.nanmin(
                    df_dia["temperature"]
                )
            )

            tmax = round(
                np.nanmax(
                    df_dia["temperature"]
                )
            )

            umidade = round(
                np.nanmin(
                    df_dia["humidity"]
                )
            )

            uv = round(
                np.nanmax(
                    df_dia["uv"]
                )
            )

            chuva = round(
                np.nansum(
                    df_dia["precipitation"]
                ),
                2
            )

            prob_chuva = round(
                np.nanmax(
                    df_dia["rain_probability"]
                )
            )

            vento = round(
                np.nanmean(
                    df_dia["wind_speed"]
                )
            )

            rajada = round(
                np.nanmax(
                    df_dia["wind_gusts"]
                )
            )

            direcao = direcao_cardinal(

                np.nanmean(
                    df_dia["wind_direction"]
                )
            )

            cape = round(
                np.nanmax(
                    df_dia["cape"]
                )
            )

            ######################################################
            ################## CLASSIFICAÇÕES ####################
            ######################################################

            condicao = classificar_chuva(
                chuva
            )

            prob_raios = calcular_prob_raios(

                cape,
                prob_chuva,
                rajada
            )

            risco = classificar_risco(

                prob_raios,
                rajada,
                chuva
            )

            ######################################################
            ################## UV ################################
            ######################################################

            categoria_uv = classificar_uv(
                uv
            )

            risco_uv = cor_uv(
                uv
            )

            ######################################################
            ################## RESULTADO #########################
            ######################################################

            lista_resultados.append({

                "estacao":
                    estacao,

                "data":
                    pd.to_datetime(dia).strftime(
                        "%d/%m/%Y"
                    ),

                "condicao":
                    condicao,

                "temp_min":
                    tmin,

                "temp_max":
                    tmax,

                "umidade":
                    umidade,

                "uv":
                    uv,

                "categoria_uv":
                    categoria_uv,

                "risco_uv":
                    risco_uv,

                "precipitacao":
                    chuva,

                "prob_chuva":
                    prob_chuva,

                "vento":
                    vento,

                "rajada":
                    rajada,

                "direcao":
                    direcao,

                "prob_raios":
                    prob_raios,

                "risco":
                    risco
            })

    except Exception as erro:

        print(
            f"Erro em {linha['Estação']}: "
            f"{erro}"
        )

##################################################################
######################## DATAFRAME FINAL #########################
##################################################################

df_final = pd.DataFrame(
    lista_resultados
)

##################################################################
######################## SALVANDO CSV ############################
##################################################################

nome_arquivo = (

    "previsoes_operacionais.csv"
)

df_final.to_csv(

    nome_arquivo,
    index=False,
    encoding="utf-8-sig"
)

##################################################################
######################## FINAL ###################################
##################################################################

print("\n")

print("="*60)

print(
    "PROCESSAMENTO FINALIZADO"
)

print("="*60)

print("\nArquivo salvo:")

print(nome_arquivo)

print("\nTotal de registros:")

print(len(df_final))

print("\nPrévia:")

print(df_final.head())