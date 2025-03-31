import streamlit as st
import pandas as pd
from utils import load_data, show_last_month_winners

# Load dataset
GLOBAL_PATH = "global_results.json"
data = load_data(GLOBAL_PATH)

# Create dataframe
df = pd.DataFrame(data)

# Show results in a table
st.dataframe(df)

# Show last months's results
show_last_month_winners()