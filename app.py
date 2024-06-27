import streamlit as st
import requests
import pandas as pd

# Definir la URL de la API
url = 'https://yields.llama.fi/pools'

# Hacer la solicitud GET a la API
response = requests.get(url, headers={'accept': '*/*'})

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    data = response.json()['data']

    # Filtrar los resultados por el proyecto "notional-v3"
    filtered_data = [pool for pool in data if pool['project'] == 'notional-v3']

    # Preparar los datos para mostrar en la tabla
    rows = []
    for pool in filtered_data:
        row = {
            'chain': pool['chain'],
            'name': pool['project'],
            'symbol': pool['symbol'],
            'tvl': pool['tvlUsd'],
            'apybase': pool['apyBase'],
            'apyreward': pool['apyReward'],
            'apy': pool['apy'],
            'pool': pool['pool'],
            'stablecoin': pool['stablecoin'],
            'exposure': pool['exposure'],
            'apymeand30d': pool['apyMean30d'],
            'pool_meta': pool['poolMeta']
        }

        # Obtener los datos de predicción y ajustar el formato
        prediction = pool['predictions']
        row['predicted_class'] = prediction['predictedClass']
        row['predicted_probability'] = prediction['predictedProbability']
        row['binned_confidence'] = prediction['binnedConfidence']

        rows.append(row)

    # Convertir los datos en un DataFrame de pandas
    df = pd.DataFrame(rows)

    # Mostrar los resultados en la aplicación Streamlit
    st.title('Resultados de la API de Yields para el proyecto "notional-v3"')
    
    if not df.empty:
        st.dataframe(df)
    else:
        st.write("No se encontraron resultados para el proyecto 'notional-v3'.")
else:
    st.write("Error al obtener los datos de la API.")
