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
if "uploader_ver" not in st.session_state:
    st.session_state["uploader_ver"] = 0

with st.sidebar:
    st.header("Settings")
    st.write("Note: The system always uses `fishing_data.xlsx` as the **unique master file**.")

    st.markdown("---")
    st.subheader("Replace Master File")
    up = st.file_uploader(
        "Replace with a compatible .xlsx",
        type=["xlsx"],
        key=f"master_uploader_{st.session_state['uploader_ver']}"
    )

    if up and st.button("Confirm Replacement", key="replace_btn"):
        try:
            incoming = pd.read_excel(up, engine="openpyxl")
            missing = [c for c in COLUMNS if c not in incoming.columns]
            if missing:
                st.error(f"Missing columns: {missing}")
            else:
                incoming = incoming.reindex(columns=COLUMNS)
                save_df(DATA_PATH, incoming)
                df_check = load_df(DATA_PATH)
                if len(df_check) == len(incoming):
                    st.success(f"Replaced successfully: {len(df_check)} rows.")
                    st.session_state["uploader_ver"] += 1
                    st.rerun()
                else:
                    st.error("Replace failed: row count mismatch.")
        except Exception as e:
            st.error(f"Unable to upload: {e}")
    # Button to Download a Copy of the Master File
    try:
        with open(DATA_PATH, "rb") as f:
            st.download_button(
                label="Download a Copy of the Master File",
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

    # ===== Button to clear or recreate the master file =====
    st.markdown("---")
    st.subheader("⚠️ Danger Zone")

    with st.expander("Clear All Master File Data", expanded=False):
        st.warning("This action will permanently delete all fishing records from `fishing_data.xlsx`.")
        admin_pass = st.text_input("Enter the admin password to confirm:", type="password", key="admin_clear")
    
        if st.button("Confirm and Clear"):
            if admin_pass == "admin":  
                save_df(DATA_PATH, pd.DataFrame(columns=COLUMNS))
                st.success("`fishing_data.xlsx` has been successfully recreated and cleared.")
            elif not admin_pass.strip():
                st.error("Please enter the admin password before confirming.")
            else:
                st.error("Incorrect password. Action denied.")


# Load master file and find the id
df_master = load_df(DATA_PATH)
next_id = get_next_id(df_master)
last_date = get_last_date(df_master)
last_fish = df_master["Fish_name"].dropna().iloc[-1] if not df_master.empty and df_master["Fish_name"].notna().any() else None

# ===== Form Values =====
with st.form("capture_form", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Date/Time & Location")
        use_id = st.text_input("Catch ID", value=str(next_id), disabled=True, help="Auto-incremented, read-only.")
        date = st.date_input("Date", value=last_date)
        time = st.time_input("Time")
        country = st.selectbox("Country", ["United States", "Canada", "Peru", "Bolivia", "Brazil", "Czech Republic", "Netherlands", "Italy", "Germany", "Ukraine", "United Kingdom", "France", "Republic of the Congo", "Mongolia", "Japan", "Maldives"])
        state = st.selectbox("State/Province", ["Texas", "Missouri", "New York", "Colorado", "North Carolina", "Oregon", "Florida", "Louisiana", "Michigan", "California", "Alaska", "Mississippi", "Alberta", "Loreto", "Beni", "Amazonas", "Central Bohemia", "North Holland", "Lazio", "Bavaria", "Dnipro", "England", "Île-de-France", "Pool", "Khövsgöl", "Wakayama", "Kaafu"])

    with col2:
        st.subheader("Weather & Conditions")
        weather = st.selectbox("Weather", ["Sunny","Partly cloudy","Cloudy","Rain","Storm","Windy","Other"])
        temp_air = st.number_input("Air temperature (°C)", min_value=-50.0, max_value=60.0, step=0.1, format="%.1f")
        temp_water = st.number_input("Water temperature (°C)", min_value=-5.0, max_value=40.0, step=0.1, format="%.1f")
        wind_ms = st.number_input("Wind (m/s)", min_value=0.0, max_value=60.0, step=0.1, format="%.1f")
        pressure = st.number_input("Atmospheric pressure (hPa)", min_value=850.0, max_value=1100.0, step=0.1, format="%.1f")

    with col3:
        st.subheader("Method & Fish Data")
        method = st.selectbox("Fishing method", ["Spinning", "Casting", "Float", "Bottom", "Other"])
        fish_name = st.selectbox("Fish Name",options=fish_list,index=fish_list.index(last_fish) if last_fish in fish_list else 0)
        fish_weight = st.number_input("Fish Weight (kg)", min_value=0.0, max_value=1000.0, step=0.01, format="%.2f")
        fish_length = st.number_input("Fish Length (cm)", min_value=0.0, max_value=1000.0, step=0.1, format="%.2f")
        fish_price = st.number_input("Sale Price", min_value=1, max_value=1_000_000, step=1)

    submitted = st.form_submit_button(f"Save Catch #{next_id}")

if submitted:
    errors = []

    if not country or not str(country).strip():
        errors.append("Country is required.")
    if not state or not str(state).strip():
        errors.append("State/Province is required.")
    if not method or not str(method).strip():
        errors.append("Fishing method is required.")
    if not fish_name or not str(fish_name).strip():
        errors.append("Fish Name is required.")

    country_states = {
        "United States": {"Texas","Missouri","New York","Colorado","North Carolina","Oregon","Florida","Louisiana","Michigan","California","Alaska","Mississippi"},
        "Canada": {"Alberta"},
        "Peru": {"Loreto"},
        "Bolivia": {"Beni"},
        "Brazil": {"Amazonas"},
        "Czech Republic": {"Central Bohemia"},
        "Netherlands": {"North Holland"},
        "Italy": {"Lazio"},
        "Germany": {"Bavaria"},
        "Ukraine": {"Dnipro"},
        "United Kingdom": {"England"},
        "France": {"Île-de-France"},
        "Republic of the Congo": {"Pool"},
        "Mongolia": {"Khövsgöl"},
        "Japan": {"Wakayama"},
        "Maldives": {"Kaafu"},
    }
    if country in country_states and state not in country_states[country]:
        errors.append(f"‘{state}’ does not belong to ‘{country}’. Please pick a valid State/Province for that country.")

    if temp_water > 40:
        errors.append("Water temperature should be ≤ 40 °C.")
    if temp_air < -50 or temp_air > 60:
        errors.append("Air temperature out of allowed range (-50 to 60 °C).")
    if wind_ms > 60 or wind_ms < 0:
        errors.append("Wind (m/s) out of allowed range (0 to 60 m/s).")
    if pressure < 850 or pressure > 1100:
        errors.append("Atmospheric pressure out of allowed range (850–1100 hPa).")


    if fish_weight <= 0:
        errors.append("Fish weight must be greater than 0 kg.")
    if fish_length <= 0:
        errors.append("Fish length must be greater than 0 cm.")
    if fish_price < 1:
        errors.append("Sale Price must be at least 1.")

    if fish_list and fish_name not in fish_list:
        errors.append("Fish name must be one from the list.")

    if errors:
        st.error("Please fix the following issues before saving:")
        for e in errors:
            st.markdown(f"- {e}")
        st.stop()
    else:
        df = load_df(DATA_PATH)
        use_id_int = int(next_id)
        new_row = {
        "Catch_id": use_id_int,
        "Date": date,
        "Time": time.strftime("%H:%M"),
        "Country": country,
        "State": state,
        "Weather": weather,
        "Temperature_in_Celsius": temp_air,
        "Water_temperature_in_Celsius": temp_water,
        "Wind_in_m/s": wind_ms,
        "Atmospheric_pressure_in_hPa": pressure,
        "Fishing_method": method,
        "Fish_name": fish_name,
        "Fish_weight_in_kg": fish_weight,
        "Fish_length_in_cm": fish_length,
        "Fish_sell_price": fish_price / 10
        }
        new_entry = pd.DataFrame([new_row])
        new_entry = new_entry[[col for col in COLUMNS if col in new_entry.columns]]

        if df is None or df.empty:
            df = new_entry
        else:
            df = pd.concat([df, new_entry], ignore_index=True)
        save_df(DATA_PATH, df)
        st.success(f"Catch #{next_id} validated successfully! Saving…")
        st.rerun()

# ===== Data View =====
ensure_file(DATA_PATH)
try:
    df_show = pd.read_excel(DATA_PATH, engine="openpyxl")
    st.subheader("Current Fishing Records")
    st.dataframe(df_show, use_container_width=True)
except Exception as e:
    st.warning(f"File cannot be read: {e}")

# ===== Rights and License =====
st.markdown("---")
st.subheader("Open-Source Project — Fishing Data Collector")
st.caption("""
Developed by **Jose Pablo Barrantes Jiménez**  
© 2025 Jose Pablo Barrantes Jiménez  

This project is open source under the MIT License.  
You are free to use, modify, and distribute this code as long as credit is given  
to the original author: Jose Pablo Barrantes Jiménez.

GitHub: [github.com/JoseP055](https://github.com/JoseP055)  
LinkedIn: [linkedin.com/in/josepbarrantes](https://www.linkedin.com/in/josep55)
""")

