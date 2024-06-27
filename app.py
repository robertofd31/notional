import streamlit as st
import requests
import pandas as pd
import altair as alt

@st.cache
def fetch_data(url):
    response = requests.get(url, headers={'accept': '*/*'})
    if response.status_code == 200:
        return response.json()['data']
    else:
        st.error("Failed to fetch data from API")
        return None

# Define the API URL
url = 'https://yields.llama.fi/pools'

# Fetch data from API
data = fetch_data(url)

if data:
    # Filter results by the project "notional-v3"
    filtered_data = [pool for pool in data if pool['project'] == 'notional-v3']

    # Prepare data for displaying in the table
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

        # Get prediction data and format it
        prediction = pool['predictions']
        row['predicted_class'] = prediction['predictedClass']
        row['predicted_probability'] = prediction['predictedProbability']

        rows.append(row)

    # Convert data to a pandas DataFrame
    df = pd.DataFrame(rows)

    # Sort by descending APY
    df = df.sort_values(by='apy', ascending=False)

    image_url = "https://pbs.twimg.com/profile_images/1327058875627970561/zk8nf4kv_400x400.jpg"

    # Contenedor para alinear verticalmente título e imagen
    st.markdown(
        f"""
        <div style="display: flex; align-items: center;">
            <img src="{image_url}" style="height: 100px; width: 100px; margin-right: 10px;">
            <h1 style="margin-bottom: 0;">Notional V3 Yields</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Filter by chain
    st.sidebar.header('Filters')
    chains = df['chain'].unique()
    all_chains_option = ["Select All"] + list(chains)
    selected_chains = st.sidebar.multiselect('Select Chain(s)', options=all_chains_option, default=["Select All"])

    if "Select All" in selected_chains:
        filtered_df = df.copy()
    else:
        filtered_df = df[df['chain'].isin(selected_chains)]

    # Filter by TVL
    min_tvl, max_tvl = df['tvl'].min(), df['tvl'].max()
    tvl_range = st.sidebar.slider('Select TVL (USD)', min_tvl, max_tvl, (min_tvl, max_tvl))
    filtered_df = filtered_df[(filtered_df['tvl'] >= tvl_range[0]) & (filtered_df['tvl'] <= tvl_range[1])]

    # Filter by APY
    min_apy, max_apy = df['apy'].min(), df['apy'].max()
    apy_range = st.sidebar.slider('Select APY', min_apy, max_apy, (min_apy, max_apy))
    filtered_df = filtered_df[(filtered_df['apy'] >= apy_range[0]) & (filtered_df['apy'] <= apy_range[1])]

    # Filter by pool_meta
    pool_meta_options = df['pool_meta'].dropna().unique()
    all_pool_meta_option = ["Select All"] + list(pool_meta_options)
    selected_pool_meta = st.sidebar.selectbox('Select Pool Meta', options=all_pool_meta_option)

    if selected_pool_meta == "Select All":
        filtered_df = filtered_df.copy()
    else:
        filtered_df = filtered_df[filtered_df['pool_meta'] == selected_pool_meta]

    if not filtered_df.empty:
        # Display results in a table
        st.subheader('Filtered Results')
        st.dataframe(filtered_df)

        # Bar chart for APY per Pool ID
        st.subheader('Bar Chart: APY per Pool ID')
        bars = alt.Chart(filtered_df).mark_bar(color='#33f8fe').encode(
            x='pool',
            y='apy',
            tooltip=['name', 'symbol', 'apy']
        ).properties(
            width=600
        ).interactive()

        st.altair_chart(bars, use_container_width=True)

    else:
        st.write('No data to display with the selected filters.')

else:
    st.write("Error fetching data from the API.")
