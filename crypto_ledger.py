import hashlib
import json
import init_db
import datetime
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()


def hash_password(password_str):
    """Generates a secure bcrypt hash for a new password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_str.encode("utf-8"), salt).decode("utf-8")


def verify_password(password_str, hashed_str):
    """Verifies a plaintext password against the stored bcrypt hash."""
    return bcrypt.checkpw(password_str.encode("utf-8"), hashed_str.encode("utf-8"))


def process_new_transfer(transfer_payload):
    """
    The master function to process a new transfer.
    It fetches the old hash, generates the new one, and saves it to the DB.
    """
    evidence_id = transfer_payload["evidence_id"]

    previous_hash = db_manager.get_latest_hash(evidence_id)
    transfer_payload["previous_hash"] = previous_hash

    current_hash = generate_row_hash(transfer_payload)
    transfer_payload["current_hash"] = current_hash

    inserted_id = db_manager.insert_transfer(transfer_payload)

    if inserted_id:
        print(f"Transfer secured and logged. Current Hash: {current_hash[:10]}...")
        return True
    else:
        print("Failed to insert transfer into database.")
        return False


def verify_evidence_ledger(evidence_id):
    """
    Audits the entire chain of custody for a single piece of evidence.
    Recalculates every hash to mathematically prove the database hasn't been tampered with.
    """
    conn = db_manager.get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT * FROM chain_of_custody 
        WHERE evidence_id = %s 
        ORDER BY transfer_id ASC
    """,
        (evidence_id,),
    )

    records = cursor.fetchall()
    conn.close()

    if not records:
        return False, "No records found for this evidence ID."

    expected_previous = "GENESIS_HASH"

    for row in records:
        if "transfer_time" in row and hasattr(row["transfer_time"], "isoformat"):
            row["transfer_time"] = row["transfer_time"].isoformat()

        if row["previous_hash"] != expected_previous:
            return (
                False,
                f"Integrity Failure: Broken chain at Transfer ID {row['transfer_id']}",
            )

        recalculated_hash = generate_row_hash(row)

        if recalculated_hash != row["current_hash"]:
            return (
                False,
                f"Tampering Detected: Hash mismatch at Transfer ID {row['transfer_id']}",
            )

        expected_previous = recalculated_hash

    return True, "Ledger is mathematically intact. All hashes verified."


def generate_file_hash(file_bytes):
    """
    Takes raw bytes from a Streamlit file upload (e.g., CCTV footage, hard drive image)
    and generates a SHA-256 hash to prove the digital evidence has not been tampered with.
    """
    file_hash = hashlib.sha256()
    file_hash.update(file_bytes)
    return file_hash.hexdigest()


def verify_digital_evidence(uploaded_file_bytes, stored_db_hash):
    """
    Compares an uploaded file against the hash stored in the database
    to verify it hasn't been corrupted or altered.
    """
    current_hash = generate_file_hash(uploaded_file_bytes)
    if current_hash == stored_db_hash:
        return True, "Match: Digital evidence is intact and untampered."
    else:
        return (
            False,
            "ALERT: File hash mismatch. This digital evidence has been altered!",
        )


def generate_row_hash(payload_dict):
    hash_data = payload_dict.copy()

    if "current_hash" in hash_data:
        del hash_data["current_hash"]
    if "transfer_id" in hash_data:
        del hash_data["transfer_id"]

    if "current_hash" in hash_data:
        del hash_data["current_hash"]

    for key, value in hash_data.items():
        if isinstance(value, (datetime.datetime, datetime.date)):
            hash_data[key] = value.isoformat()

    salt = os.getenv("SECRET_KEY", "default_salt")
    row_string = json.dumps(hash_data, sort_keys=True) + salt

    return hashlib.sha256(row_string.encode("utf-8")).hexdigest()


def verify_entire_system_integrity():
    """
    Global System Audit: Fetches every piece of evidence
    and verifies its entire chain of custody.
    """
    evidence_list = db_manager.get_all_evidence()
    system_status = True
    report = []

    for ev in evidence_list:
        ev_id = ev["evidence_id"]
        is_valid, message = verify_evidence_ledger(ev_id)

        status_str = "Pass" if is_valid else "Fail"
        db_manager.log_audit_result(ev_id, message, status_str)

        if not is_valid:
            system_status = False

        report.append({"evidence_id": ev_id, "status": status_str, "message": message})

    return system_status, report
