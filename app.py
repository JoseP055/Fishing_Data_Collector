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

# ===== Sidebar: Master File Management =====

with st.sidebar:
    st.header("Configuration")
    st.write("Note: The system always uses `fishing_data.xlsx` as the **unique master file**.")

    # Upload a new Excel file to replace the master
    uploaded_file = st.file_uploader("Replace the master file with a compatible Excel file", type=["xlsx"])
    if uploaded_file is not None:
        try:
            incoming = pd.read_excel(uploaded_file, engine="openpyxl")
            # Validate minimum required columns (extra columns are allowed)
            missing_columns = [c for c in COLUMNS if c not in incoming.columns]
            if missing_columns:
                st.error(f"The uploaded file is not compatible. Missing columns: {missing_columns}")
            else:
                # Reorder columns: base columns first, then any extras
                column_order = COLUMNS + [c for c in incoming.columns if c not in COLUMNS]
                incoming = incoming[column_order]
                save_df(DATA_PATH, incoming)
                st.success("Master file successfully replaced.")
        except Exception as e:
            st.error(f"Unable to upload Excel file: {e}")

    # Button to clear or recreate the master file
    if st.button("Clear all master file data"):
        save_df(DATA_PATH, pd.DataFrame(columns=COLUMNS))
        st.success("`fishing_data.xlsx` has been successfully recreated.")

    # Button to download a copy of the master file
    try:
        with open(DATA_PATH, "rb") as f:
            st.download_button(
                label="Download a copy of the master file",
                data=f,
                file_name="fishing_data_copy.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except FileNotFoundError:
        st.warning("No master file found to download.")

    st.info(
        "Note: The master file is always **a single version** stored on the server (`fishing_data.xlsx`). "
        "Use this download option only for reference copies."
    )
