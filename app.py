import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

# ===== Config =====
DATA_PATH = Path("fishing_data.xlsx")  
COLUMNS = ["Catch_id","Date","Time","Country","State","Weather","Temperature_in_Celsius","Water_temperature_in_Celsius","Wind_in_m/s", "Fishing_method", "Fish_name", "Fish_weight_in_kg", "Fish_length_in_cm", "Fish_sell_price"]


st.set_page_config(page_title="Data Capture → Excel", page_icon="📗", layout="centered")
st.title("Data Capture → Excel")

# ===== Helpers =====
def ensure_file(path: Path):
    if not path.exists():
        pd.DataFrame(columns=COLUMNS).to_excel(path, index=False, engine="openpyxl")

def load_df(path: Path) -> pd.DataFrame:
    ensure_file(path)
    try:
        return pd.read_excel(path, engine="openpyxl")
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def save_df(path: Path, df: pd.DataFrame):
    df.to_excel(path, index=False, engine="openpyxl")


