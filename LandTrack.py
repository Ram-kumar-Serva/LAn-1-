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

# --- UI Setup ---
st.set_page_config(layout="wide", page_title="Rent Tracker", page_icon="🏠")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { color: white; background-color: #262730; }
    </style>
""", unsafe_allow_html=True)

st.title("🏠 Rent Tracker")

# --- Load Data ---
properties_df = pd.read_csv(PROPERTY_FILE)
rent_df = pd.read_csv(RENT_FILE)
renters_df = pd.read_csv(RENTER_FILE)

# --- Navigation ---
st.sidebar.header("Navigation")
nav = st.sidebar.radio("Go to", ["🏘️ Home", "📄 Rent Records", "➕ Add Property", "📁 Export"])

# --- Home Page: Display Properties ---
if nav == "🏘️ Home":
    st.subheader("Rental Properties")
    cols = st.columns(3)
    for idx, row in properties_df.iterrows():
        with cols[idx % 3]:
            latest_rent = rent_df[(rent_df['Property Name'] == row['Property Name']) & 
                                  (rent_df['Month'] == datetime.datetime.now().month) & 
                                  (rent_df['Year'] == datetime.datetime.now().year)]
            rent_received = not latest_rent.empty
            rent_status = "🟢 ₹" + str(row['Lease Amount']) if rent_received else "🟠 ₹" + str(row['Lease Amount'])
            if st.button(f"{row['Property Name']}\n{row['Renter Name']}\n{rent_status}", key=idx):
                if not rent_received:
                    with st.form(f"rent_form_{idx}"):
                        st.write(f"Enter rent received info for: **{row['Property Name']}**")
                        received_date = st.date_input("Date Received", datetime.date.today())
                        payment_mode = st.text_input("Payment Mode (optional)")
                        submitted = st.form_submit_button("Submit")
                        if submitted:
                            rent_df.loc[len(rent_df)] = {
                                'Property Name': row['Property Name'],
                                'Date Received': received_date,
                                'Amount': row['Lease Amount'],
                                'Payment Mode': payment_mode,
                                'Month': received_date.month,
                                'Year': received_date.year
                            }
                            rent_df.to_csv(RENT_FILE, index=False)
                            st.success("Rent record added!")

# --- Add Property ---
if nav == "➕ Add Property":
    st.subheader("Add a New Property")
    with st.form("add_property_form"):
        pname = st.text_input("Property Name")
        renter = st.text_input("Renter Name")
        contact = st.text_input("Renter Contact Info (optional)")
        lease_amt = st.number_input("Lease Amount", step=500)
        lease_start = st.date_input("Lease Start Date")
        rent_day = st.number_input("Expected Rent Day (1-31)", min_value=1, max_value=31)
        increase_type = st.selectbox("Yearly Increase Type", ["%", "Fixed"])
        increase_value = st.number_input("Increase Value", step=100)
        submit = st.form_submit_button("Add Property")
        if submit:
            new_row = {
                'Property Name': pname,
                'Renter Name': renter,
                'Contact Info': contact,
                'Lease Amount': lease_amt,
                'Lease Start Date': lease_start,
                'Expected Rent Day': rent_day,
                'Increase Type': increase_type,
                'Increase Value': increase_value
            }
            properties_df = properties_df.append(new_row, ignore_index=True)
            properties_df.to_csv(PROPERTY_FILE, index=False)
            renters_df = renters_df.append({'Renter Name': renter, 'Contact Info': contact}, ignore_index=True)
            renters_df.to_csv(RENTER_FILE, index=False)
            st.success("Property added successfully!")

# --- Rent Records ---
if nav == "📄 Rent Records":
    st.subheader("Rent Payment Records")
    selected_property = st.selectbox("Filter by Property", ["All"] + list(properties_df['Property Name'].unique()))
    filtered = rent_df
    if selected_property != "All":
        filtered = rent_df[rent_df['Property Name'] == selected_property]
    st.dataframe(filtered)

# --- Export ---
if nav == "📁 Export":
    st.subheader("Export All Data")
    with pd.ExcelWriter("Rent_Tracker_Export.xlsx") as writer:
        properties_df.to_excel(writer, sheet_name="Properties", index=False)
        rent_df.to_excel(writer, sheet_name="Rent Records", index=False)
        renters_df.to_excel(writer, sheet_name="Renters", index=False)
    with open("Rent_Tracker_Export.xlsx", "rb") as f:
        st.download_button("Download Excel File", f, "Rent_Tracker_Export.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
