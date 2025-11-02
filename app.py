import streamlit as st
import pandas as pd
from datetime import datetime, date
from pathlib import Path
from fish_list import fish_list
import os

# ===== Config =====
DATA_PATH = Path("fishing_data.xlsx")
COLUMNS = [
    "Catch_id","Date","Time","Country","State","Weather","Temperature_in_Celsius",
    "Water_temperature_in_Celsius","Wind_in_m/s", "Atmospheric_pressure_in_hPa", "Fishing_method", "Fish_name",
    "Fish_weight_in_kg", "Fish_length_in_cm", "Fish_sell_price"
]

st.set_page_config(page_title="Fishing Data Capture → Excel", page_icon="", layout="centered")
st.title("Fishing Data Capture → Excel")

# ===== Helpers =====
def ensure_file(path: Path):
    if not path.exists():
        pd.DataFrame(columns=COLUMNS).to_excel(path, index=False, engine="openpyxl")

def load_df(path: Path) -> pd.DataFrame:
    ensure_file(path)
    try:
        df = pd.read_excel(path, engine="openpyxl")
        # Normaliza el orden de columnas (agrega faltantes si el archivo vino externo)
        for c in COLUMNS:
            if c not in df.columns:
                df[c] = pd.Series(dtype="object")
        return df[COLUMNS]
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def save_df(path: Path, df: pd.DataFrame):
    df.to_excel(path, index=False, engine="openpyxl")

def get_next_id(df: pd.DataFrame) -> int:
    if df.empty or df["Catch_id"].dropna().empty:
        return 1
    return int(pd.to_numeric(df["Catch_id"], errors="coerce").dropna().max()) + 1

def get_last_date(df: pd.DataFrame):
    """Return the most recent date in the 'Date' column, or today's date if empty."""
    if df.empty or df["Date"].dropna().empty:
        return date.today()
    try:
        last_date = pd.to_datetime(df["Date"], errors="coerce").dropna().max().date()
        return last_date
    except Exception:
        return date.today()

# ===== Sidebar: Master File Management =====
with st.sidebar:
    st.header("Configuration")
    st.write("Note: The system always uses `fishing_data.xlsx` as the **unique master file**.")

    # Upload a new Excel file to replace the master
    uploaded_file = st.file_uploader("Replace the master file with a compatible Excel file", type=["xlsx"])
    if uploaded_file is not None:
        try:
            incoming = pd.read_excel(uploaded_file, engine="openpyxl")
            missing_columns = [c for c in COLUMNS if c not in incoming.columns]
            if missing_columns:
                st.error(f"The uploaded file is not compatible. Missing columns: {missing_columns}")
            else:
                column_order = COLUMNS + [c for c in incoming.columns if c not in COLUMNS]
                incoming = incoming[column_order]
                save_df(DATA_PATH, incoming[COLUMNS])  # guarda solo columnas del maestro
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

# Load master file and find the id
df_master = load_df(DATA_PATH)
next_id = get_next_id(df_master)
last_date = get_last_date(df_master)
last_fish = df_master["Fish_name"].dropna().iloc[-1] if not df_master.empty and df_master["Fish_name"].notna().any() else None

# ===== Form Values =====
with st.form("capture_form", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Datetime and Location")
        st.text_input("Catch ID", value=str(next_id), disabled=True, help="Auto-incremented, read-only.")
        date = st.date_input("Date", value=last_date)
        time = st.time_input("Time", value=datetime.now().replace(second=0, microsecond=0).time())
        country = st.selectbox("Country", ["United States", "Canada", "Peru", "Bolivia", "Brazil", "Czech Republic", "Netherlands", "Italy", "Germany", "Ukraine", "United Kingdom", "France", "Republic of the Congo", "Mongolia", "Japan", "Maldives"])
        state = st.selectbox("State/Province", ["Texas", "Missouri", "New York", "Colorado", "North Carolina", "Oregon", "Florida", "Louisiana", "Michigan", "California", "Alaska", "Mississippi", "Alberta", "Loreto", "Beni", "Amazonas", "Central Bohemia", "North Holland", "Lazio", "Bavaria", "Dnipro", "England", "Île-de-France", "Pool", "Khövsgöl", "Wakayama", "Kaafu"])

    with col2:
        st.subheader("Time conditions")
        weather = st.selectbox("Weather", ["Sunny","Partly cloudy","Cloudy","Rain","Storm","Windy","Other"])
        temp_air = st.number_input("Air temperature (°C)", min_value=-50.0, max_value=60.0, step=0.1, format="%.1f")
        temp_water = st.number_input("Water temperature (°C)", min_value=-5.0, max_value=40.0, step=0.1, format="%.1f")
        wind_ms = st.number_input("Wind (m/s)", min_value=0.0, max_value=60.0, step=0.1, format="%.1f")
        pressure = st.number_input("Atmospheric pressure (hPa)", min_value=850.0, max_value=1100.0, step=0.1, format="%.1f")

    with col3:
        st.subheader("Method and Fish data")
        method = st.selectbox("Fishing method", ["Spinning", "Casting", "Float", "Bottom", "Other"])
        fish_name = st.selectbox("Fish name",options=fish_list,index=fish_list.index(last_fish) if last_fish in fish_list else 0)
        fish_weight = st.number_input("Fish weight (kg)", min_value=0.0, max_value=1000.0, step=0.01, format="%.2f")
        fish_length = st.number_input("Fish length (cm)", min_value=0.0, max_value=1000.0, step=0.1, format="%.2f")
        fish_price = st.number_input("Fish sell price", min_value=1, max_value=1_000_000, step=1)

    submitted = st.form_submit_button(f"Save Catch #{next_id}")