
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

    # Filtrar los resultados por el proyecto "notional"
    filtered_data = [pool for pool in data if pool['project'] == 'notional-v3']

    # Convertir los datos filtrados en un DataFrame de pandas
    df = pd.DataFrame(filtered_data)

    # Mostrar los resultados en la aplicación Streamlit
    st.title('Resultados de la API de Yields para el proyecto "notional"')
    
    if not df.empty:
        st.dataframe(df)
    else:
        st.write("No se encontraron resultados para el proyecto 'notional'.")
else:
    st.write("Error al obtener los datos de la API.")
