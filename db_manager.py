import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


def get_db_connection():
    """Establish connection to the MySQL server using environment variables."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        auth_plugin="mysql_native_password",
    )


def get_latest_hash(evidence_id):
    """Fetches the CurrentHash of the most recent transfer for a specific item."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT current_hash 
        FROM chain_of_custody 
        WHERE evidence_id = %s 
        ORDER BY transfer_id DESC 
        LIMIT 1
    """,
        (evidence_id,),
    )
    result = cursor.fetchone()

    conn.close()
    return result["current_hash"] if result else "GENESIS_HASH"


def insert_transfer(payload):
    """Inserts a newly hashed transfer payload into the MySQL database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO chain_of_custody (
                evidence_id, transferred_by_badge, received_by_badge, 
                reason, transfer_time, previous_hash, current_hash
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            (
                payload["evidence_id"],
                payload["transferred_by_badge"],
                payload["received_by_badge"],
                payload["reason"],
                payload["transfer_time"],
                payload["previous_hash"],
                payload["current_hash"],
            ),
        )
        conn.commit()
        last_id = cursor.lastrowid
        return last_id
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
        return None
    finally:
        conn.close()


def insert_personnel(badge, first, last, dept, clearance):
    """Helper function to seed the database with users."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO personnel (badge_number, first_name, last_name, department, clearance_level)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (badge, first, last, dept, clearance),
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"DB Error inserting personnel: {e}")
        return False
    finally:
        conn.close()


def get_all_personnel():
    """Fetches personnel for Streamlit Dropdowns."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT badge_number, first_name, last_name FROM personnel")
    results = cursor.fetchall()
    conn.close()
    return results


def insert_storage_location(location_id, facility, room, storage_type, req_temp):
    """Adds a new storage location (e.g., Freezer A)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO storage_locations (location_id, facility_name, room_number, storage_type, requires_temp_monitoring)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (location_id, facility, room, storage_type, req_temp),
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"DB Error inserting storage: {e}")
        return False
    finally:
        conn.close()


def get_all_storage_locations():
    """Fetches storage locations for Streamlit Dropdowns."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT location_id, facility_name, room_number FROM storage_locations"
    )
    results = cursor.fetchall()
    conn.close()
    return results


def insert_case(case_id, investigator_badge, status, created_at):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO cases (case_id, lead_investigator_badge, status, created_at)
            VALUES (%s, %s, %s, %s)
        """,
            (case_id, investigator_badge, status, created_at),
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"DB Error inserting case: {e}")
        return False
    finally:
        conn.close()


def get_all_cases():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT case_id, status FROM cases")
    results = cursor.fetchall()
    conn.close()
    return results


def insert_evidence(payload):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO evidence (
                evidence_id, item_type, description, collection_location, 
                collected_by_badge, collected_at, digital_hash, current_location_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                payload["evidence_id"],
                payload["item_type"],
                payload["description"],
                payload["collection_location"],
                payload["collected_by_badge"],
                payload["collected_at"],
                payload["digital_hash"],
                payload["current_location_id"],
            ),
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"DB Error inserting evidence: {e}")
        return False
    finally:
        conn.close()


def get_all_evidence():
    """Fetches evidence items to populate the Transfer Custody dropdown."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT evidence_id, description FROM evidence")
    results = cursor.fetchall()
    conn.close()
    return results


def link_evidence_to_case(case_id, evidence_id, linked_by_badge, notes):
    """Junction table insert: Links one piece of evidence to multiple cases."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO case_evidence_map (case_id, evidence_id, linked_by_badge, link_date, notes)
            VALUES (%s, %s, %s, NOW(), %s)
        """,
            (case_id, evidence_id, linked_by_badge, notes),
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"DB Error linking case/evidence: {e}")
        return False
    finally:
        conn.close()


def log_lab_analysis_request(evidence_id, requested_by_badge, test_type):
    """Requests a lab test (e.g., DNA, Toxicology) for an item."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO lab_analysis (evidence_id, requested_by_badge, test_type, request_date)
            VALUES (%s, %s, %s, NOW())
        """,
            (evidence_id, requested_by_badge, test_type),
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"DB Error requesting lab analysis: {e}")
        return False
    finally:
        conn.close()


def log_legal_disposition(
    evidence_id, action_type, authorized_by_badge, witnessed_by_badge, court_order
):
    """Update to include the required witness parameter."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO legal_dispositions (evidence_id, action_type, authorized_by_badge, witnessed_by_badge, action_date, court_order_reference)
            VALUES (%s, %s, %s, %s, NOW(), %s)
        """,
            (
                evidence_id,
                action_type,
                authorized_by_badge,
                witnessed_by_badge,
                court_order,
            ),
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"DB Error logging disposition: {e}")
        return False
    finally:
        conn.close()


def get_full_chain_of_custody(evidence_id):
    """Fetches the CoC history with actual officer names for court reporting."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT c.transfer_time, c.reason, 
               p1.last_name AS transferred_by_name, 
               p2.last_name AS received_by_name, 
               c.current_hash
        FROM chain_of_custody c
        JOIN personnel p1 ON c.transferred_by_badge = p1.badge_number
        JOIN personnel p2 ON c.received_by_badge = p2.badge_number
        WHERE c.evidence_id = %s
        ORDER BY c.transfer_time ASC
    """,
        (evidence_id,),
    )
    results = cursor.fetchall()
    conn.close()
    return results


def get_dashboard_stats():
    """Returns counts for the main UI dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    stats = {}

    cursor.execute("SELECT COUNT(*) FROM cases")
    stats["total_cases"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM evidence")
    stats["total_evidence"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM lab_analysis WHERE status = 'Pending'")
    stats["pending_labs"] = cursor.fetchone()[0]

    conn.close()
    return stats


def search_evidence(search_query):
    """Allows searching evidence by description or ID."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM evidence WHERE evidence_id LIKE %s OR description LIKE %s"
    params = (f"%{search_query}%", f"%{search_query}%")
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results


def get_cases_for_evidence(evidence_id):
    """Retrieves all cases linked to a specific piece of evidence (Junction Query)."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT c.* FROM cases c
        JOIN case_evidence_map m ON c.case_id = m.case_id
        WHERE m.evidence_id = %s
    """
    cursor.execute(query, (evidence_id,))
    results = cursor.fetchall()
    conn.close()
    return results


def log_audit_result(evidence_id, result_message, status):
    """Logs the results of a cryptographic integrity check."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO system_audit_logs (evidence_id, result_message, status, audit_time)
            VALUES (%s, %s, %s, NOW())
        """,
            (evidence_id, result_message, status),
        )
        conn.commit()
    finally:
        conn.close()


def update_lab_results(request_id, summary, file_path, equipment):
    """Updates a pending lab request with final results."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE lab_analysis 
            SET result_summary = %s, report_file_path = %s, 
                equipment_used = %s, status = 'Completed', completed_at = NOW()
            WHERE request_id = %s
        """,
            (summary, file_path, equipment, request_id),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def log_temperature(location_id, temp):
    """Records a temperature reading for environmental evidence preservation."""
    conn = get_db_connection()
    cursor = conn.cursor()
    alert = True if temp > -10.0 else False
    try:
        cursor.execute(
            """
            INSERT INTO temperature_logs (location_id, recorded_at, temperature_celsius, alert_triggered)
            VALUES (%s, NOW(), %s, %s)
        """,
            (location_id, temp, alert),
        )
        conn.commit()
    finally:
        conn.close()


def insert_personnel(badge, username, password_hash, first, last, dept, clearance):
    """Helper function to create new officer accounts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO personnel (badge_number, username, password_hash, first_name, last_name, department, clearance_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            (badge, username, password_hash, first, last, dept, clearance),
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"DB Error inserting personnel: {e}")
        return False
    finally:
        conn.close()


def authenticate_officer(username, password_str):
    """Checks credentials and returns the user record if valid."""
    import crypto_ledger

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM personnel WHERE username = %s AND status = 'Active'", (username,)
    )
    user = cursor.fetchone()
    conn.close()

    if user and crypto_ledger.verify_password(password_str, user["password_hash"]):
        return user
    return None


def get_full_evidence_registry():
    """Fetches all evidence fields for the dashboard registry display."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT evidence_id, item_type, description, current_location_id FROM evidence"
    )
    results = cursor.fetchall()
    conn.close()
    return results


def get_items_needing_attention():
    """Fetches items in temporary/improvised storage or with failed cryptographic audits."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT e.evidence_id, e.description, l.storage_type AS current_security_status
        FROM evidence e
        JOIN storage_locations l ON e.current_location_id = l.location_id
        WHERE l.storage_type LIKE '%Temporary%' 
        OR l.storage_type LIKE '%Holding%'
        OR e.evidence_id IN (
            SELECT evidence_id FROM system_audit_logs WHERE status = 'Fail'
        )
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


def get_full_storage_locations():
    """Fetches all storage location data for the management UI."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM storage_locations")
    results = cursor.fetchall()
    conn.close()
    return results

def get_temp_monitored_locations():
    """Fetches only locations that require temperature monitoring."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT location_id, facility_name, room_number FROM storage_locations WHERE requires_temp_monitoring = TRUE"
    )
    results = cursor.fetchall()
    conn.close()
    return results

def get_pending_lab_requests():
    """Fetches all lab requests that are currently pending."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT request_id, evidence_id, test_type, request_date FROM lab_analysis WHERE status = 'Pending'")
    results = cursor.fetchall()
    conn.close()
    return results

def update_case(case_id, new_status, new_lead_badge):
    """Updates the status and lead investigator of an existing case."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE cases 
            SET status = %s, lead_investigator_badge = %s
            WHERE case_id = %s
        """,
            (new_status, new_lead_badge, case_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"DB Error updating case: {e}")
        return False
    finally:
        conn.close()