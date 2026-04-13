import streamlit as st
import pandas as pd
import crypto_ledger
import db_manager
import datetime
from fpdf import FPDF


def generate_pdf_report(ev_id, history):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(
        200, 10, txt=f"Official Chain of Custody Report: {ev_id}", ln=True, align="C"
    )
    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    for record in history:
        line = f"[{record['transfer_time']}] {record['reason']} | From: {record['transferred_by_name']} To: {record['received_by_name']}"
        pdf.multi_cell(0, 10, txt=line)
        pdf.set_font("Courier", size=8)
        pdf.cell(0, 10, txt=f"Hash: {record['current_hash']}", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.ln(2)
    return pdf.output(dest="S").encode("latin-1")


st.set_page_config(page_title="Forensic CoC System", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

if not st.session_state["logged_in"]:
    st.title("⚖️ Forensic Evidence System - Authentication")

    tab1, tab2 = st.tabs(["Secure Login", "Register Officer"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                user = db_manager.authenticate_officer(username, password)
                if user:
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = user
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab2:
        st.info("Register a new officer account into the system.")
        with st.form("register_form"):
            r_badge = st.text_input("Badge Number (e.g., B-101)")
            r_user = st.text_input("Username")
            r_pass = st.text_input("Password", type="password")
            r_first = st.text_input("First Name")
            r_last = st.text_input("Last Name")
            r_dept = st.selectbox(
                "Department",
                ["Homicide", "Major Crimes", "Lab Tech", "Evidence Control"],
            )
            r_submit = st.form_submit_button("Register Account")

            if r_submit:
                if not (r_badge and r_user and r_pass and r_first and r_last):
                    st.warning("All fields are required.")
                else:
                    hashed_pw = crypto_ledger.hash_password(r_pass)
                    if db_manager.insert_personnel(
                        r_badge, r_user, hashed_pw, r_first, r_last, r_dept, 1
                    ):
                        st.success("Account successfully created! You can now log in.")
                    else:
                        st.error(
                            "Failed to create account. Badge number or Username may already exist."
                        )

    st.stop()

user_data = st.session_state["current_user"]
st.sidebar.success(
    f"Logged in as: {user_data['first_name']} {user_data['last_name']} ({user_data['badge_number']})"
)
if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state["current_user"] = None
    st.rerun()

st.title("⚖️ Forensic Evidence & Chain of Custody System")
st.markdown("Cryptographically Secured Evidence Management")

menu = st.sidebar.selectbox(
    "System Modules",
    [
        "Dashboard",
        "Log New Evidence",
        "Transfer Custody",
        "Audit & Verify Ledger",
        "Digital Evidence Verification",
        "Manage Facilities",
    ],
)

if menu == "Dashboard":
    st.subheader("System Overview")
    stats = db_manager.get_dashboard_stats()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cases", stats.get("total_cases", 0))
    col2.metric("Evidence Logged", stats.get("total_evidence", 0))
    col3.metric("Pending Lab Requests", stats.get("pending_labs", 0))

    st.divider()
    st.info(
        "Welcome to the secure portal. Navigate using the sidebar to log evidence or initiate transfers."
    )

    dash_col1, dash_col2 = st.columns(2)

    with dash_col1:
        st.subheader("📋 Evidence Registry")
        search_query = st.text_input("Search Registry by ID or Description")

        if search_query:
            results = db_manager.search_evidence(search_query)
        else:
            results = db_manager.get_full_evidence_registry()

        if results:
            df_reg = pd.DataFrame(results)
            df_reg.columns = [col.replace("_", " ").title() for col in df_reg.columns]
            st.dataframe(df_reg, use_container_width=True, height=350)
        else:
            st.info("No items found in the registry.")

    with dash_col2:
        st.subheader("⚠️ Needs Attention")
        st.write(
            "Items in improvised security (temporary holding) or with flagged audits."
        )

        attn_items = db_manager.get_items_needing_attention()

        if attn_items:
            df_attn = pd.DataFrame(attn_items)
            df_attn.columns = [col.replace("_", " ").title() for col in df_attn.columns]

            st.dataframe(
                df_attn.style.applymap(
                    lambda x: "background-color: #ffcccc; color: black;"
                ),
                use_container_width=True,
                height=350,
            )
        else:
            st.success("All evidence is properly secured and audited.")

elif menu == "Log New Evidence":
    st.subheader("📦 Intake New Evidence")

    personnel = db_manager.get_all_personnel()
    locations = db_manager.get_all_storage_locations()

    officer_options = {
        f"{p['badge_number']} - {p['first_name']} {p['last_name']}": p["badge_number"]
        for p in personnel
    }
    location_options = {
        f"{l['facility_name']} ({l['room_number']})": l["location_id"]
        for l in locations
    }

    if not officer_options or not location_options:
        st.error(
            "🚨 System Data Missing: No personnel or storage locations found in database."
        )
        st.info(
            "Please run 'python reset_system.py' in your terminal and refresh this page."
        )
        st.stop()

    with st.form("intake_form"):
        ev_id = st.text_input("Evidence ID (e.g., EV-1001)")
        item_type = st.selectbox("Item Type", ["Physical", "Biological", "Digital"])
        description = st.text_area("Item Description")
        collection_loc = st.text_input("Collection Location / GPS")

        uploaded_file = st.file_uploader(
            "Upload Digital Item (Optional)", type=["jpg", "pdf", "mp4", "zip", "png"]
        )

        col1, col2 = st.columns(2)
        with col1:
            collected_by = st.selectbox(
                "Collected By", options=list(officer_options.keys())
            )
        with col2:
            storage_loc = st.selectbox(
                "Initial Storage Location", options=list(location_options.keys())
            )

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
                    "current_location_id": location_options[storage_loc],
                }

                if db_manager.insert_evidence(payload):
                    genesis_payload = {
                        "evidence_id": ev_id,
                        "transferred_by_badge": officer_options[collected_by],
                        "received_by_badge": officer_options[collected_by],
                        "reason": "Initial Evidence Intake & Seizure",
                        "transfer_time": datetime.datetime.utcnow().replace(
                            microsecond=0
                        ),
                    }
                    crypto_ledger.process_new_transfer(genesis_payload)
                    st.success(
                        f"✅ Evidence {ev_id} logged and cryptographically sealed!"
                    )
                else:
                    st.error(
                        "Failed to log evidence. Check if the Evidence ID already exists."
                    )

elif menu == "Transfer Custody":
    st.subheader("🔗 Record a Chain of Custody Transfer")
    st.warning("Warning: Once submitted, this record is cryptographically sealed.")

    evidence_items = db_manager.get_all_evidence()
    personnel = db_manager.get_all_personnel()

    ev_options = {
        f"{e['evidence_id']} - {e['description'][:30]}": e["evidence_id"]
        for e in evidence_items
    }
    officer_options = {
        f"{p['badge_number']} - {p['last_name']}": p["badge_number"] for p in personnel
    }

    with st.form("transfer_form"):
        selected_ev = st.selectbox("Select Evidence", options=ev_options.keys())

        col1, col2 = st.columns(2)
        with col1:
            transferred_by = st.selectbox(
                "Relinquished By", options=officer_options.keys()
            )
        with col2:
            received_by = st.selectbox(
                "Received By",
                options=officer_options.keys(),
                index=1 if len(officer_options) > 1 else 0,
            )

        reason = st.selectbox(
            "Reason for Transfer",
            [
                "Transport to Lab",
                "Ballistics",
                "Toxicology",
                "Court Appearance",
                "Return to Storage",
            ],
        )
        submit = st.form_submit_button("Seal & Record Transfer")

        if submit:
            transfer_payload = {
                "evidence_id": ev_options[selected_ev],
                "transferred_by_badge": officer_options[transferred_by],
                "received_by_badge": officer_options[received_by],
                "reason": reason,
                "transfer_time": datetime.datetime.utcnow().replace(microsecond=0),
            }
            if crypto_ledger.process_new_transfer(transfer_payload):
                st.success("✅ Transfer Cryptographically Sealed and Logged!")
            else:
                st.error("❌ System Error: Transfer failed to write to database.")

elif menu == "Audit & Verify Ledger":
    st.subheader("🛡️ Verify Ledger Integrity (Court View)")

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

                    report_data = generate_pdf_report(audit_ev_id, history)
                    st.download_button(
                        label="📄 Download Court Report (PDF)",
                        data=report_data,
                        file_name=f"CoC_Report_{audit_ev_id}.pdf",
                        mime="application/pdf",
                    )
            else:
                st.error(f"🚨 ALERT: {message}")

elif menu == "Digital Evidence Verification":
    st.subheader("🖥️ Digital Integrity Check")
    st.write("Upload a file to verify its hash against the court-recorded value.")

    evidence_items = db_manager.get_all_evidence()
    ev_options = {f"{e['evidence_id']}": e["evidence_id"] for e in evidence_items}
    selected_ev = st.selectbox("Select Digital Evidence ID", options=ev_options.keys())

    uploaded_file = st.file_uploader("Upload File (CCTV, Disk Image, etc.)")

    if uploaded_file and selected_ev:
        evidence_data = db_manager.search_evidence(selected_ev)[0]
        stored_hash = evidence_data["digital_hash"]

        if st.button("Verify File Integrity"):
            file_bytes = uploaded_file.getvalue()
            is_valid, message = crypto_ledger.verify_digital_evidence(
                file_bytes, stored_hash
            )

            if is_valid:
                st.success(f"✅ {message}")
            else:
                st.error(f"🚨 {message}")

elif menu == "Manage Facilities":
    st.subheader("🏢 Facility Management")
    st.write("Register new secure storage locations, freezers, and lockboxes.")

    with st.form("new_location_form"):
        col1, col2 = st.columns(2)

        with col1:
            loc_id = st.text_input("Location ID (e.g., LOC-Z1)")
            facility = st.text_input("Facility Name (e.g., Annex, Precinct 9)")

        with col2:
            room = st.text_input("Room / Identifier (e.g., Room 10, Garage B)")
            storage_type = st.selectbox(
                "Storage Type",
                [
                    "Secure Shelf",
                    "Deep Freezer",
                    "Biohazard Refrigerator",
                    "Chemical Fridge",
                    "Temporary Holding Locker",
                    "Long-Term Bin",
                    "Weapons Lockbox",
                    "Faraday Locker",
                    "Vehicle Impound",
                    "Other",
                ],
            )

        req_temp = st.checkbox("Requires Temperature Monitoring")

        submit_loc = st.form_submit_button("Register Location")

        if submit_loc:
            if not loc_id or not facility or not room:
                st.warning("Please fill out the Location ID, Facility Name, and Room.")
            else:
                if db_manager.insert_storage_location(
                    loc_id, facility, room, storage_type, req_temp
                ):
                    st.success(f"✅ Location '{loc_id}' successfully registered!")
                else:
                    st.error(
                        "Failed to register location. Ensure the Location ID is unique."
                    )

    st.divider()

    st.subheader("Current Storage Locations")
    locations = db_manager.get_full_storage_locations()

    if locations:
        df_loc = pd.DataFrame(locations)
        df_loc.columns = [col.replace("_", " ").title() for col in df_loc.columns]
        st.dataframe(df_loc, use_container_width=True)
    else:
        st.info("No storage locations found in the system.")
