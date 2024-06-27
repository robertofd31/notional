import streamlit as st
import requests
import pandas as pd
import altair as alt

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

        rows.append(row)

    # Convertir los datos en un DataFrame de pandas
    df = pd.DataFrame(rows)

    # Ordenar por APY descendente
    df = df.sort_values(by='apy', ascending=False)

    # Mostrar los resultados en la aplicación Streamlit
    st.title('Resultados de la API de Yields para el proyecto "notional-v3"')
    
    if not df.empty:
        st.dataframe(df)

        # Gráfico dinámico según filtros
        st.subheader('Gráfico Dinámico')

        # Filtrar por cadena (chain)
        chains = df['chain'].unique()
        selected_chain = st.selectbox('Seleccionar Chain', chains)
        filtered_df = df[df['chain'] == selected_chain] if selected_chain else df

        # Filtrar por TVL
        min_tvl, max_tvl = df['tvl'].min(), df['tvl'].max()
        tvl_range = st.slider('Seleccionar TVL (USD)', min_tvl, max_tvl, (min_tvl, max_tvl))
        filtered_df = filtered_df[(filtered_df['tvl'] >= tvl_range[0]) & (filtered_df['tvl'] <= tvl_range[1])]

        # Filtrar por APY
        min_apy, max_apy = df['apy'].min(), df['apy'].max()
        apy_range = st.slider('Seleccionar APY', min_apy, max_apy, (min_apy, max_apy))
        filtered_df = filtered_df[(filtered_df['apy'] >= apy_range[0]) & (filtered_df['apy'] <= apy_range[1])]

        # Filtrar por pool_meta
        pool_meta_options = df['pool_meta'].dropna().unique()
        selected_pool_meta = st.selectbox('Seleccionar Pool Meta', pool_meta_options)
        filtered_df = filtered_df[filtered_df['pool_meta'] == selected_pool_meta] if selected_pool_meta else filtered_df

        # Mostrar el gráfico dinámico
        if not filtered_df.empty:
            chart = alt.Chart(filtered_df).mark_circle().encode(
                x='apy',
                y='tvl',
                color='chain',
                tooltip=['name', 'symbol', 'apy', 'tvl']
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.write('No hay datos que mostrar con los filtros seleccionados.')

    else:
        st.write("No se encontraron resultados para el proyecto 'notional-v3'.")
else:
    st.write("Error al obtener los datos de la API.")
