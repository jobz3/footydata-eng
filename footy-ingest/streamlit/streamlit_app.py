import streamlit as st
import duckdb
from pathlib import Path

DB_PATH = '/home/jobze/Desktop/data-engineering-course/footydata-eng/footy-ingest/data/footy_data.duckdb'

@st.cache_resource
def get_connection():
    try:
        connect = duckdb.connect(DB_PATH, read_only=True)
    except Exception as e:
        print("Error Occurred: ", e)
        return
    return connect

con = get_connection()

st.title("Footy Data | Football Standings")

competition = st.selectbox(
    "Competition",
    options = ['PL', 'BL1', 'SA', 'FL1'],
    format_func = lambda x: {"PL": "Premier League", "BL1": "Bundesliga", "SA": "Serie A", "FL1": "Ligue 1"}[x]
)

df = con.execute("""
    SELECT 
        position as '#',
        "team_name" as "Team",
        "played_games" as "GP",
        "won" as "W",
        "draw" as "D",
        "lost" as "L",
        "points" as "Pts",
        "goals_for" as "GF",
        "goals_against" as "GA"
    FROM standings_pl
    WHERE competition_code = ?
    ORDER BY position ASC
                 
""", [competition]).df()

st.dataframe(df, hide_index = True, use_container_width = True)