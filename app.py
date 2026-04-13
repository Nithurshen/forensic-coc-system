import streamlit as st
import pandas as pd
import crypto_ledger
import db_manager
import datetime
from fpdf import FPDF

def generate_pdf_report(ev_id, history):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Official Chain of Custody Report: {ev_id}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    for record in history:
        line = f"[{record['transfer_time']}] {record['reason']} | From: {record['transferred_by_name']} To: {record['received_by_name']}"
        pdf.multi_cell(0, 10, txt=line)
        pdf.set_font("Courier", size=8)
        pdf.cell(0, 10, txt=f"Hash: {record['current_hash']}", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1')

st.set_page_config(page_title="Forensic CoC System", layout="wide")

st.title("⚖️ Forensic Evidence & Chain of Custody System")
st.markdown("Cryptographically Secured Evidence Management")

menu = st.sidebar.selectbox("System Modules", [
    "Dashboard", 
    "Log New Evidence", 
    "Transfer Custody", 
    "Audit & Verify Ledger",
    "Evidence Registry"
])

if menu == "Dashboard":
    st.subheader("System Overview")
    stats = db_manager.get_dashboard_stats()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cases", stats.get('total_cases', 0))
    col2.metric("Evidence Logged", stats.get('total_evidence', 0))
    col3.metric("Pending Lab Requests", stats.get('pending_labs', 0))
    
    st.divider()
    st.info("Welcome to the secure portal. Navigate using the sidebar to log evidence or initiate transfers.")

elif menu == "Log New Evidence":
    st.subheader("📦 Intake New Evidence")
    
    # Fetch data for dropdowns
    personnel = db_manager.get_all_personnel()
    locations = db_manager.get_all_storage_locations()
    
    # CRITICAL: Build options only if data exists to avoid KeyError: None
    officer_options = {f"{p['badge_number']} - {p['first_name']} {p['last_name']}": p['badge_number'] for p in personnel}
    location_options = {f"{l['facility_name']} ({l['room_number']})": l['location_id'] for l in locations}

    if not officer_options or not location_options:
        st.error("🚨 System Data Missing: No personnel or storage locations found in database.")
        st.info("Please run 'python reset_system.py' in your terminal and refresh this page.")
        st.stop() # Stop execution to prevent the crash below

    with st.form("intake_form"):
        ev_id = st.text_input("Evidence ID (e.g., EV-1001)")
        item_type = st.selectbox("Item Type", ["Physical", "Biological", "Digital"])
        description = st.text_area("Item Description")
        collection_loc = st.text_input("Collection Location / GPS")
        
        uploaded_file = st.file_uploader("Upload Digital Item (Optional)", type=['jpg', 'pdf', 'mp4', 'zip', 'png'])
        
        col1, col2 = st.columns(2)
        with col1:
            collected_by = st.selectbox("Collected By", options=list(officer_options.keys()))
        with col2:
            storage_loc = st.selectbox("Initial Storage Location", options=list(location_options.keys()))
            
        submit = st.form_submit_button("Log Evidence into System")
        
        if submit:
            if not ev_id or not description:
                st.warning("Please provide an Evidence ID and Description.")
            else:
                d_hash = None
                if uploaded_file:
                    d_hash = crypto_ledger.generate_file_hash(uploaded_file.getvalue())

                payload = {
                    "evidence_id": ev_id,
                    "item_type": item_type,
                    "description": description,
                    "collection_location": collection_loc,
                    "collected_by_badge": officer_options[collected_by],
                    "collected_at": datetime.datetime.utcnow(),
                    "digital_hash": d_hash,
                    "current_location_id": location_options[storage_loc]
                }
                
                if db_manager.insert_evidence(payload):
                    # AUTOMATIC GENESIS TRANSFER
                    genesis_payload = {
                        "evidence_id": ev_id,
                        "transferred_by_badge": officer_options[collected_by],
                        "received_by_badge": officer_options[collected_by],
                        "reason": "Initial Evidence Intake & Seizure",
                        "transfer_time": datetime.datetime.utcnow().replace(microsecond=0)
                    }
                    crypto_ledger.process_new_transfer(genesis_payload)
                    st.success(f"✅ Evidence {ev_id} logged and cryptographically sealed!")
                else:
                    st.error("Failed to log evidence. Check if the Evidence ID already exists.")

elif menu == "Transfer Custody":
    st.subheader("🔗 Record a Chain of Custody Transfer")
    st.warning("Warning: Once submitted, this record is cryptographically sealed.")
    
    # Fetch real data for dropdowns
    evidence_items = db_manager.get_all_evidence()
    personnel = db_manager.get_all_personnel()
    
    ev_options = {f"{e['evidence_id']} - {e['description'][:30]}": e['evidence_id'] for e in evidence_items}
    officer_options = {f"{p['badge_number']} - {p['last_name']}": p['badge_number'] for p in personnel}
    
    with st.form("transfer_form"):
        selected_ev = st.selectbox("Select Evidence", options=ev_options.keys())
        
        col1, col2 = st.columns(2)
        with col1:
            transferred_by = st.selectbox("Relinquished By", options=officer_options.keys())
        with col2:
            received_by = st.selectbox("Received By", options=officer_options.keys(), index=1 if len(officer_options)>1 else 0)
            
        reason = st.selectbox("Reason for Transfer", ["Transport to Lab", "Ballistics", "Toxicology", "Court Appearance", "Return to Storage"])
        submit = st.form_submit_button("Seal & Record Transfer")
        
        if submit:
            transfer_payload = {
                "evidence_id": ev_options[selected_ev],
                "transferred_by_badge": officer_options[transferred_by],
                "received_by_badge": officer_options[received_by],
                "reason": reason,
                "transfer_time": datetime.datetime.utcnow().replace(microsecond=0)
            }
            if crypto_ledger.process_new_transfer(transfer_payload):
                st.success("✅ Transfer Cryptographically Sealed and Logged!")
            else:
                st.error("❌ System Error: Transfer failed to write to database.")

elif menu == "Audit & Verify Ledger":
    st.subheader("🛡️ Verify Ledger Integrity (Court View)")
    
    # CRITICAL: This line defines the variable before the button uses it
    audit_ev_id = st.text_input("Enter Evidence ID to Audit:")
    
    if st.button("Run Cryptographic Audit"):
        if audit_ev_id:
            is_valid, message = crypto_ledger.verify_evidence_ledger(audit_ev_id)
            if is_valid:
                st.success(f"✅ {message}")
                history = db_manager.get_full_chain_of_custody(audit_ev_id)
                if history:
                    st.write("### Immutable Timeline")
                    st.dataframe(pd.DataFrame(history))
                    
                    # Generate PDF Report
                    report_data = generate_pdf_report(audit_ev_id, history)
                    st.download_button(
                        label="📄 Download Court Report (PDF)",
                        data=report_data,
                        file_name=f"CoC_Report_{audit_ev_id}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error(f"🚨 ALERT: {message}")

elif menu == "Digital Evidence Verification":
    st.subheader("🖥️ Digital Integrity Check")
    st.write("Upload a file to verify its hash against the court-recorded value.")
    
    # 1. Select the evidence item
    evidence_items = db_manager.get_all_evidence()
    ev_options = {f"{e['evidence_id']}": e['evidence_id'] for e in evidence_items}
    selected_ev = st.selectbox("Select Digital Evidence ID", options=ev_options.keys())
    
    # 2. Upload the file to check
    uploaded_file = st.file_uploader("Upload File (CCTV, Disk Image, etc.)")
    
    if uploaded_file and selected_ev:
        # Fetch the hash originally stored in the DB
        # Note: You may need Dev 1 to write a quick helper: db_manager.get_evidence_by_id()
        evidence_data = db_manager.search_evidence(selected_ev)[0] 
        stored_hash = evidence_data['digital_hash']
        
        if st.button("Verify File Integrity"):
            file_bytes = uploaded_file.getvalue()
            is_valid, message = crypto_ledger.verify_digital_evidence(file_bytes, stored_hash)
            
            if is_valid:
                st.success(f"✅ {message}")
            else:
                st.error(f"🚨 {message}")

elif menu == "Evidence Registry":
    st.subheader("📋 Evidence Registry")
    st.write("View and search all items currently logged in the system.")

    # 1. Search Bar UI
    search_query = st.text_input("Search by Evidence ID or Description", placeholder="e.g., Glock or EV-1001")

    # 2. Logic to fetch data
    if search_query:
        # Uses the LIKE %query% logic from your db_manager
        results = db_manager.search_evidence(search_query)
        st.caption(f"Showing results for: '{search_query}'")
    else:
        # Default view showing everything
        results = db_manager.get_all_evidence()

    # 3. Display Results
    if results:
        df = pd.DataFrame(results)
        # Clean up column names for the UI
        df.columns = [col.replace('_', ' ').title() for col in df.columns]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No items found in the registry.")