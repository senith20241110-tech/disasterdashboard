#natural disaster dashboard
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Global Natural Disasters Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("emdat-country-profiles_2026_04_24.xlsx", sheet_name=0, header=1)
    df.columns = ["Year","Country","ISO","Disaster_Group","Disaster_Subgroup",
                  "Disaster_Type","Disaster_Subtype","Total_Events",
                  "Total_Affected","Total_Deaths","Total_Damage_Original",
                  "Total_Damage_Adjusted","CPI"]
    df = df[df["Year"].apply(lambda x: str(x).isdigit())]
    df["Year"] = df["Year"].astype(int)
    df["Total_Deaths"] = pd.to_numeric(df["Total_Deaths"], errors="coerce")
    df["Total_Affected"] = pd.to_numeric(df["Total_Affected"], errors="coerce")
    df["Total_Events"] = pd.to_numeric(df["Total_Events"], errors="coerce")
    df["Total_Damage_Adjusted"] = pd.to_numeric(df["Total_Damage_Adjusted"], errors="coerce")
    return df

df = load_data()

st.title("Global Natural Disasters Dashboard")
st.markdown("Interactive analysis of natural disasters worldwide using EM-DAT data.")

st.sidebar.header("Filters")
year_range = st.sidebar.slider("Year Range", int(df["Year"].min()), int(df["Year"].max()), (2000, 2023))
disaster_types = st.sidebar.multiselect("Disaster Type", sorted(df["Disaster_Type"].dropna().unique()), default=None)
countries = st.sidebar.multiselect("Country", sorted(df["Country"].dropna().unique()), default=None)

filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
if disaster_types:
    filtered = filtered[filtered["Disaster_Type"].isin(disaster_types)]
if countries:
    filtered = filtered[filtered["Country"].isin(countries)]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Events", int(filtered["Total_Events"].sum()))
col2.metric("Total Deaths", int(filtered["Total_Deaths"].sum()))
col3.metric("Total Affected", f'{int(filtered["Total_Affected"].sum()):,}')
col4.metric("Countries Affected", filtered["Country"].nunique())

st.markdown("---")

st.subheader("Disaster Events Over Time")
events_by_year = filtered.groupby("Year")["Total_Events"].sum().reset_index()
fig1 = px.line(events_by_year, x="Year", y="Total_Events", title="Total Disaster Events Per Year")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Deaths by Disaster Type")
deaths_by_type = filtered.groupby("Disaster_Type")["Total_Deaths"].sum().reset_index().sort_values("Total_Deaths", ascending=False).head(10)
fig2 = px.bar(deaths_by_type, x="Disaster_Type", y="Total_Deaths", title="Top 10 Deadliest Disaster Types", color="Total_Deaths")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Total People Affected by Country")
map_data = filtered.groupby(["Country","ISO"])["Total_Affected"].sum().reset_index()
fig3 = px.choropleth(map_data, locations="ISO", color="Total_Affected",
                     hover_name="Country", title="Total Affected Per Country",
                     color_continuous_scale="Reds")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Disaster Type Breakdown")
type_counts = filtered.groupby("Disaster_Type")["Total_Events"].sum().reset_index()
fig4 = px.pie(type_counts, names="Disaster_Type", values="Total_Events", title="Share of Events by Disaster Type")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Top 10 Most Affected Countries")
top_countries = filtered.groupby("Country")["Total_Affected"].sum().reset_index().sort_values("Total_Affected", ascending=False).head(10)
fig5 = px.bar(top_countries, x="Country", y="Total_Affected", title="Top 10 Countries by People Affected", color="Total_Affected")
st.plotly_chart(fig5, use_container_width=True)

if st.checkbox("Show raw data"):
    st.dataframe(filtered)
