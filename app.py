import streamlit as st
import requests
import pandas as pd
import altair as alt

# Define the API URL
url = 'https://yields.llama.fi/pools'

# Make a GET request to the API
response = requests.get(url, headers={'accept': '*/*'})

# Check if the request was successful
if response.status_code == 200:
    data = response.json()['data']

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

    # Display results in the Streamlit app
    st.title('Yields API Results for project "notional-v3"')

    # Filter by chain
    st.sidebar.header('Filters')
    chains = df['chain'].unique()
    selected_chain = st.sidebar.selectbox('Select Chain', chains)
    filtered_df = df[df['chain'] == selected_chain] if selected_chain else df

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
    selected_pool_meta = st.sidebar.selectbox('Select Pool Meta', pool_meta_options)
    filtered_df = filtered_df[filtered_df['pool_meta'] == selected_pool_meta] if selected_pool_meta else filtered_df

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
