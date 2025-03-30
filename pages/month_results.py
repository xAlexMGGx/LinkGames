import streamlit as st
import pandas as pd
from utils import load_data, convert_table, show_last_day_winners

# Load dataset
MONTH_PATH = "month_results.json"
data = load_data(MONTH_PATH)

# Dropdown to select type of dataset
data_type = st.selectbox(
    "Tipo de tabla",
    ("Letras", "Números"),
    index=0,
    placeholder="Escoge el tipo de tabla",
)

# Create dataframe
if data_type != "Letras" and data_type != "Números":
    st.error("Opción no válida")
else:
    if data_type == "Números":
        data = convert_table(data)
    df = pd.DataFrame(data)

# Show results in a table
st.dataframe(df)

# Load last day's results
show_last_day_winners()