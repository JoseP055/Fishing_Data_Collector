# Fishing Data Collector
A simple and scalable data collection web app built with **Python** and **Streamlit**, designed to record and manage fishing-related data in a single **Excel file** (`fishing_data.xlsx`). Perfect for researchers, anglers, or organizations who want to centralize and analyze field data without complex databases.

# Overview
Fishing Data Collector provides a clean and intuitive interface to log fishing records — such as the fisher’s name, date, catch category, amount, and additional notes — directly into an Excel sheet. The app ensures that all records are stored in one master file, making it easy to scale, update, and maintain your dataset over time.

# Features
- Simple web interface built with Streamlit  
- Stores all records in one master Excel file (`fishing_data.xlsx`)  
- No duplicates or extra downloads — one version of truth  
- Upload and replace your master file anytime  
- Reset or clean data with a single click  
- Ready for analytics, dashboards, and Power BI integration  

# Installation
## 1. Clone this repository
```bash
git clone https://github.com/jospaba12/Fishing_Data_Collector.git
cd Fishing_Data_Collector
```
# (Optional) Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# or on macOS/Linux:
# source .venv/bin/activate
```

# Install dependencies
```bash
pip install -r requirements.txt
```
# Run the app

```bash
streamlit run app.py
```
# Open your browser

Go to http://localhost:8501

You will see the interface to start logging your data.

# How It Works

1. Fill in the form fields.
2. Click “Save” — the record is stored in `fishing_data.xlsx`.
3. You can view all records directly in the app.
4. Use the sidebar to:
   - Replace the master Excel file with an updated version.
   - Recreate or clean the master file (reset all data).
5. No duplicate files are created. The app updates the same `fishing_data.xlsx` file each time.

---

# Tech Stack

- **Python 3.9+**
- **Streamlit** – for the web interface  
- **Pandas** – for data manipulation  
- **OpenPyXL** – for Excel integration  

---

# Example Use Cases

- Field researchers collecting ecological or environmental data  
- Fishing clubs recording catches and weather conditions  
- Conservation projects tracking species over time  
- Data analysts testing ETL and dashboard pipelines  

---

# Future Improvements

- Add record editing and deletion per ID  
- Integrate with Power BI dashboards  
- Export to CSV or Google Sheets  
- Add user authentication for multi-user environments  

---

# Author

**Developed by:**  
Jose Pablo Barrantes Jiménez  
Founder and Director of **Evidens CR**

**Email:** jospaba12@gmail.com  
**Phone:** +506 8338 9426  
**LinkedIn:** [linkedin.com/in/josep55](https://linkedin.com/in/josep55)