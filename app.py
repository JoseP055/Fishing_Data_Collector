import streamlit as st
import pandas as pd
from datetime import datetime, date
from pathlib import Path
from fish_list import fish_list
import os
import re

# ===== Config =====
DATA_PATH = Path("fishing_data.xlsx")
SHEET_NAME = "Fishing_data"
COLUMNS = [
    "Catch_id","Date","Time","Country","State","Weather","Temperature_in_Celsius",
    "Water_temperature_in_Celsius","Wind_in_m/s", "Atmospheric_pressure_in_hPa", "Fishing_method", "Fish_name",
    "Fish_weight_in_kg", "Fish_length_in_cm", "Fish_sell_price"
]

st.set_page_config(page_title="Fishing Data Capture → Excel", page_icon="", layout="centered")
st.title("Fishing Data Capture → Excel")

# ===== Helpers =====
def ensure_file(path: Path):
    """Crea el archivo base con hoja 'Fishing_data' si no existe."""
    if not path.exists():
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            pd.DataFrame(columns=COLUMNS).to_excel(writer, index=False, sheet_name=SHEET_NAME)

def load_df(path: Path) -> pd.DataFrame:
    ensure_file(path)
    try:
        df = pd.read_excel(path, engine="openpyxl", sheet_name=SHEET_NAME)
        for c in COLUMNS:
            if c not in df.columns:
                df[c] = pd.Series(dtype="object")
        return df[COLUMNS]
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def save_df(path: Path, df: pd.DataFrame):
    with pd.ExcelWriter(path, engine="openpyxl", mode="w") as writer:
        df.to_excel(writer, index=False, sheet_name=SHEET_NAME)

def get_next_id(df: pd.DataFrame) -> int:
    if df.empty or df["Catch_id"].dropna().empty:
        return 1
    return int(pd.to_numeric(df["Catch_id"], errors="coerce").dropna().max()) + 1

def get_last_date(df: pd.DataFrame):
    if df.empty or df["Date"].dropna().empty:
        return date.today()
    try:
        return pd.to_datetime(df["Date"], errors="coerce").dropna().max().date()
    except Exception:
        return date.today()

def get_last_time(df: pd.DataFrame, fallback: str = "12:00") -> str:
    if df.empty or df["Time"].dropna().empty:
        return fallback
    try:
        last_time_raw = str(df["Time"].dropna().iloc[-1]).strip()
        if re.match(r"^(?:[01]?\d|2[0-3]):[0-5]\d$", last_time_raw):
            h, m = last_time_raw.split(":")
            return f"{int(h):02d}:{int(m):02d}"
        dt = pd.to_datetime(last_time_raw, errors="coerce")
        if pd.notnull(dt):
            return dt.strftime("%H:%M")
    except Exception:
        pass
    return fallback

def normalize_time(raw: str) -> str | None:
    """Convierte entradas flexibles como '7', '7:5', '19' → HH:MM."""
    raw = raw.strip()
    if not raw:
        return None
    match = re.match(r"^(\d{1,2})(?::?(\d{1,2}))?$", raw)
    if not match:
        return None
    h = int(match.group(1))
    m = int(match.group(2)) if match.group(2) else 0
    if 0 <= h <= 23 and 0 <= m <= 59:
        return f"{h:02d}:{m:02d}"
    return None

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
            incoming = pd.read_excel(up, engine="openpyxl", sheet_name=0)
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

    st.info("Master file sheet name: **Fishing_data** (always used internally).")

    st.markdown("---")
    st.subheader("⚠️ Danger Zone")

    with st.expander("Clear All Master File Data", expanded=False):
        st.warning("This action will permanently delete all fishing records.")
        admin_pass = st.text_input("Enter admin password:", type="password", key="admin_clear")
        if st.button("Confirm and Clear"):
            if admin_pass == "admin":
                save_df(DATA_PATH, pd.DataFrame(columns=COLUMNS))
                st.success("Master file cleared and recreated.")
            elif not admin_pass.strip():
                st.error("Please enter the admin password before confirming.")
            else:
                st.error("Incorrect password.")

# ===== Form =====
df_master = load_df(DATA_PATH)
next_id = get_next_id(df_master)
last_date = get_last_date(df_master)
last_fish = df_master["Fish_name"].dropna().iloc[-1] if not df_master.empty and df_master["Fish_name"].notna().any() else None

with st.form("capture_form", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Date/Time & Location")
        use_id = st.text_input("Catch ID", value=str(next_id), disabled=True)
        date_val = st.date_input("Date", value=last_date)

        default_time = st.session_state.get("last_time", get_last_time(df_master, "12:00"))
        time_text = st.text_input("Time (HH:MM)", value=default_time, help="Formato flexible: 7, 7:5, 07:05, 19")

        country = st.selectbox("Country", [
            "United States","Canada","Peru","Bolivia","Brazil","Czech Republic",
            "Netherlands","Italy","Germany","Ukraine","United Kingdom","France",
            "Republic of the Congo","Mongolia","Japan","Maldives"
        ])
        state = st.selectbox("State/Province", [
            "Texas","Missouri","New York","Colorado","North Carolina","Oregon",
            "Florida","Louisiana","Michigan","California","Alaska","Mississippi",
            "Alberta","Loreto","Beni","Amazonas","Central Bohemia","North Holland",
            "Lazio","Bavaria","Dnipro","England","Île-de-France","Pool","Khövsgöl",
            "Wakayama","Kaafu"
        ])

    with col2:
        st.subheader("Weather & Conditions")
        weather = st.selectbox("Weather", ["Sunny","Partly cloudy","Cloudy","Rain","Storm","Windy","Other"])
        temp_air = st.number_input("Air temperature (°C)", -50.0, 60.0, step=0.1, format="%.1f")
        temp_water = st.number_input("Water temperature (°C)", -5.0, 40.0, step=0.1, format="%.1f")
        wind_ms = st.number_input("Wind (m/s)", 0.0, 60.0, step=0.1, format="%.1f")
        pressure = st.number_input("Atmospheric pressure (hPa)", 850.0, 1100.0, step=0.1, format="%.1f")

    with col3:
        st.subheader("Method & Fish Data")
        method = st.selectbox("Fishing method", ["Spinning","Casting","Float","Bottom","Other"])
        fish_name = st.selectbox("Fish Name", options=fish_list, index=fish_list.index(last_fish) if last_fish in fish_list else 0)
        fish_weight = st.number_input("Fish Weight (kg)", 0.0, 1000.0, step=0.01, format="%.2f")
        fish_length = st.number_input("Fish Length (cm)", 0.0, 1000.0, step=0.1, format="%.2f")
        fish_price = st.number_input("Sale Price", 1, 1_000_000, step=1)

    submitted = st.form_submit_button(f"Save Catch #{next_id}")

if submitted:
    errors = []
    normalized_time = normalize_time(str(time_text))
    if not normalized_time:
        errors.append("Invalid time format. Use HH:MM or simple numeric (e.g., 7:5 → 07:05).")

    if not country: errors.append("Country is required.")
    if not state: errors.append("State/Province is required.")
    if fish_weight <= 0: errors.append("Fish weight must be greater than 0.")
    if fish_length <= 0: errors.append("Fish length must be greater than 0.")

    if errors:
        st.error("Please fix the following issues:")
        for e in errors:
            st.markdown(f"- {e}")
        st.stop()

    new_row = {
        "Catch_id": int(next_id),
        "Date": date_val,
        "Time": normalized_time,
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

    df = load_df(DATA_PATH)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_df(DATA_PATH, df)
    st.session_state["last_time"] = normalized_time
    st.success(f"Catch #{next_id} saved successfully!")
    st.rerun()

# ===== Data View =====
ensure_file(DATA_PATH)
try:
    df_show = pd.read_excel(DATA_PATH, engine="openpyxl", sheet_name=SHEET_NAME)
    st.subheader("Current Fishing Records")
    st.dataframe(df_show, use_container_width=True)
except Exception as e:
    st.warning(f"File cannot be read: {e}")

# ===== Footer =====
st.markdown("---")
st.subheader("Open-Source Project — Fishing Data Collector")
st.caption("""
Developed by **Jose Pablo Barrantes Jiménez**  
© 2025 Jose Pablo Barrantes Jiménez  

This project is open source under the MIT License.  
GitHub: [github.com/JoseP055](https://github.com/JoseP055)  
LinkedIn: [linkedin.com/in/josepbarrantes](https://www.linkedin.com/in/josep55)
""")
