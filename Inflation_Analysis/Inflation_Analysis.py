import streamlit as st
import pandas as pd
import cufflinks as cf
import plotly.graph_objs as go

cf.go_offline()
cf.set_config_file(offline=False, world_readable=True)

@st.cache_data
def load_data():
    df = pd.read_csv(r"API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_713244.csv", skiprows=4)
    meta_country = pd.read_csv(r"Metadata_Country_API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_713244.csv")
    df.columns = df.columns.str.strip()
    df = df[df["Indicator Code"] == "FP.CPI.TOTL.ZG"]
    df_merge = df.merge(meta_country, on="Country Code", how="left")
    return df_merge

df_merge = load_data()

st.sidebar.title("Inflation Data Explorer")
selected_region = st.sidebar.selectbox("Select Region", ["All"] + sorted(df_merge["Region"].dropna().unique().tolist()))
selected_income = st.sidebar.selectbox("Select Income Group", ["All"] + sorted(df_merge["IncomeGroup"].dropna().unique().tolist()))
selected_years = st.sidebar.slider("Select Year Range", 1960, 2024, (2000, 2020))

df_filtered = df_merge.copy()
if selected_region != "All":
    df_filtered = df_filtered[df_filtered["Region"] == selected_region]
if selected_income != "All":
    df_filtered = df_filtered[df_filtered["IncomeGroup"] == selected_income]

year_cols = [str(y) for y in range(selected_years[0], selected_years[1] + 1)]
df_filtered = df_filtered[["Country Name"] + year_cols]

st.title("Inflation Trends Explorer")
st.write(f"Showing inflation from {selected_years[0]} to {selected_years[1]}")

df_plot = df_filtered.set_index("Country Name").T
df_plot.index = df_plot.index.astype(int)
df_plot = df_plot.apply(pd.to_numeric, errors='coerce')  # Ensure numeric

fig = go.Figure()
for country in df_plot.columns:
    fig.add_trace(go.Scatter(
        x=df_plot.index,
        y=df_plot[country],
        mode='lines+markers',
        name=country
    ))

fig.update_layout(
    title='Inflation Trends by Country',
    xaxis_title='Year',
    yaxis_title='Inflation Rate (%)',
    template='plotly_white',
    height=600
)

st.plotly_chart(fig, use_container_width=True)
