import streamlit as st
import pandas as pd
import datetime
import os

# --- Initialize Data Files ---
PROPERTY_FILE = "properties.csv"
RENT_FILE = "rent_records.csv"
RENTER_FILE = "renters.csv"

# Ensure files exist with correct headers
if not os.path.exists(PROPERTY_FILE):
    pd.DataFrame(columns=[
        'Property Name', 'Renter Name', 'Contact Info', 'Lease Amount',
        'Lease Start Date', 'Expected Rent Day', 'Increase Type', 'Increase Value'
    ]).to_csv(PROPERTY_FILE, index=False)

if not os.path.exists(RENT_FILE):
    pd.DataFrame(columns=[
        'Property Name', 'Date Received', 'Amount', 'Payment Mode', 'Month', 'Year'
    ]).to_csv(RENT_FILE, index=False)

if not os.path.exists(RENTER_FILE):
    pd.DataFrame(columns=['Renter Name', 'Contact Info']).to_csv(RENTER_FILE, index=False)

]).to_csv(RENT_FILE, index=False)

if not os.path.exists(RENTER_FILE):
pd.DataFrame(columns=['Renter Name', 'Contact Info']).to_csv(RENTER_FILE, index=False)

# --- Load Data ---
properties_df = pd.read_csv(PROPERTY_FILE)
rent_df = pd.read_csv(RENT_FILE)
renter_df = pd.read_csv(RENTER_FILE)

# --- Helpers ---
def get_rent_status(property_name):
today = datetime.date.today()
rent_row = rent_df[(rent_df['Property Name'] == property_name) &
(rent_df['Month'] == today.month) &
(rent_df['Year'] == today.year)]
return not rent_row.empty

def calculate_current_rent(row):
lease_date = pd.to_datetime(row['Lease Start Date'])
months_elapsed = (datetime.datetime.now().year - lease_date.year)
base = row['Lease Amount']
try:
base = float(base)
except:
return base

if row['Increase Type'] == '%':
return round(base * ((1 + float(row['Increase Value'])/100) ** months_elapsed))
else:
return round(base + (float(row['Increase Value']) * months_elapsed))

# --- UI ---
st.set_page_config(page_title="🏠 Rent Tracker", layout="wide")
st.markdown("""<style>body { background-color: #121212; color: white; }</style>""", unsafe_allow_html=True)

st.title("🏠 Rent Tracker")

col1, col2 = st.columns([1, 5])

with col1:
if st.button("📊 Rent Record"):
with st.expander("All Rent Records", expanded=True):
filt = st.selectbox("Filter by Property", options=["All"] + list(properties_df['Property Name'].unique()))
if filt != "All":
df = rent_df[rent_df['Property Name'] == filt]
else:
df = rent_df
st.dataframe(df)

with col2:
if st.button("➕ Add Property"):
with st.form("Add Property Form", clear_on_submit=True):
pname = st.text_input("Property Name")
rname = st.text_input("Renter Name")
cinfo = st.text_input("Contact Info (optional)")
lamount = st.number_input("Lease Amount", min_value=0)
ldate = st.date_input("Lease Start Date")
eday = st.slider("Expected Rent Day Each Month", 1, 31, 5)

with st.expander("Advanced Options"):
inc_type = st.radio("Increase Type", ["%", "Fixed"], index=0)
inc_value = st.number_input("Increase Value (e.g., 5% or 1000/year)", min_value=0.0)

submitted = st.form_submit_button("Add")
if submitted:
new_row = pd.DataFrame([{
'Property Name': pname,
'Renter Name': rname,
'Contact Info': cinfo,
'Lease Amount': lamount,
'Lease Start Date': ldate,
'Expected Rent Day': eday,
'Increase Type': inc_type,
'Increase Value': inc_value
}])
new_row.to_csv(PROPERTY_FILE, mode='a', header=False, index=False)
st.success("Property Added!")
st.experimental_rerun()

# --- Property Cards ---
st.markdown("## 🏘️ Properties")
cols = st.columns(3)

for i, row in properties_df.iterrows():
with cols[i % 3]:
st.markdown("""
<div style='padding:10px; margin:10px; background-color:#1e1e1e; border-radius:10px;'>
""", unsafe_allow_html=True)

st.markdown(f"### {row['Property Name']}")
st.markdown(f"<small>👤 {row['Renter Name']}</small>", unsafe_allow_html=True)
rent_status = get_rent_status(row['Property Name'])
rent = calculate_current_rent(row)
color = "#00FF00" if rent_status else "#FFA500"
st.markdown(f"<h4 style='color:{color}'>💰 ₹{rent}</h4>", unsafe_allow_html=True)

if not rent_status:
if st.button(f"Mark Paid - {row['Property Name']}"):
with st.form(f"pay_{i}"):
date = st.date_input("Date Received", datetime.date.today())
mode = st.text_input("Mode of Payment (optional)")
submit = st.form_submit_button("Save")
if submit:
rent_df.loc[len(rent_df)] = [
row['Property Name'], date, rent, mode, date.month, date.year
]
rent_df.to_csv(RENT_FILE, index=False)
st.success("Rent Recorded!")
st.experimental_rerun()

st.markdown("</div>", unsafe_allow_html=True)

# --- Export ---
if st.button("📁 Export to Excel"):
with pd.ExcelWriter("rent_tracker_export.xlsx") as writer:
properties_df.to_excel(writer, sheet_name="Properties", index=False)
rent_df.to_excel(writer, sheet_name="Rent Transactions", index=False)
renter_df.to_excel(writer, sheet_name="Renter Info", index=False)
st.success("Exported to rent_tracker_export.xlsx")
