import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

# ===== Config =====
DATA_PATH = Path("fishing_data.xlsx")  
COLUMNS = ["Catch_id","Date","Time","Country","State","Weather","Temperature_in_Celsius","Water_temperature_in_Celsius","Wind_in_m/s", "Fishing_method", "Fish_name", "Fish_weight_in_kg", "Fish_length_in_cm", "Fish_sell_price"]


st.set_page_config(page_title="Data Capture → Excel", page_icon="📗", layout="centered")
st.title("Data Capture → Excel")

