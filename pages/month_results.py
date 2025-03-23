import streamlit as st
import pandas as pd

# Load dataset
with open("./data/month_results.json", "rb") as f:
    data = pd.read_json(f)

# Create dataframe
df = pd.DataFrame(data)

# Show results in a table
st.dataframe(df)
