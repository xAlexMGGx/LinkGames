import streamlit as st
import pandas as pd
from utils import load_data

# Load dataset
MONTH_PATH = "month_results.json"
data = load_data(MONTH_PATH)

# Create dataframe
df = pd.DataFrame(data)

# Show results in a table
st.dataframe(df)
