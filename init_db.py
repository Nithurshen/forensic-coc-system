import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


def get_connection():
    """Establish connection to the MySQL server using environment variables."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        auth_plugin='mysql_native_password'
    )


def initialize_database():
    print("Connecting to MySQL server...")

    temp_conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        auth_plugin='mysql_native_password'
    )
    temp_cursor = temp_conn.cursor()
    temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
    temp_conn.close()

    conn = get_connection()
    cursor = conn.cursor()

    print("Dropping existing tables for a clean reset...")
    # Drop tables in reverse order of dependencies
    tables_to_drop = [
        "system_audit_logs", "legal_dispositions", "temperature_logs",
        "lab_analysis", "chain_of_custody", "case_evidence_map",
        "evidence", "storage_locations", "cases", "personnel"
    ]
    for table in tables_to_drop:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    print("Building tables...")

    print("Building tables...")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS personnel (
        badge_number VARCHAR(50) PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        department VARCHAR(100) NOT NULL,
        clearance_level INT DEFAULT 1,
        status VARCHAR(50) DEFAULT 'Active'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        case_id VARCHAR(255) PRIMARY KEY,
        lead_investigator_badge VARCHAR(50) NOT NULL,
        status VARCHAR(50) DEFAULT 'Open',
        created_at DATETIME NOT NULL,
        FOREIGN KEY (lead_investigator_badge) REFERENCES personnel(badge_number)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS storage_locations (
        location_id VARCHAR(100) PRIMARY KEY,
        facility_name VARCHAR(100) NOT NULL,
        room_number VARCHAR(50) NOT NULL,
        storage_type VARCHAR(50) NOT NULL,
        requires_temp_monitoring BOOLEAN DEFAULT FALSE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence (
        evidence_id VARCHAR(255) PRIMARY KEY,
        item_type VARCHAR(100) NOT NULL,
        description TEXT NOT NULL,
        collection_location VARCHAR(255) NOT NULL,
        collected_by_badge VARCHAR(50) NOT NULL,
        collected_at DATETIME NOT NULL,
        digital_hash VARCHAR(255),
        current_location_id VARCHAR(100) NOT NULL,
        FOREIGN KEY (collected_by_badge) REFERENCES personnel(badge_number),
        FOREIGN KEY (current_location_id) REFERENCES storage_locations(location_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS case_evidence_map (
        map_id INT AUTO_INCREMENT PRIMARY KEY,
        case_id VARCHAR(255) NOT NULL,
        evidence_id VARCHAR(255) NOT NULL,
        linked_by_badge VARCHAR(50) NOT NULL,
        link_date DATETIME NOT NULL,
        notes TEXT,
        FOREIGN KEY (case_id) REFERENCES cases(case_id),
        FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id),
        FOREIGN KEY (linked_by_badge) REFERENCES personnel(badge_number)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chain_of_custody (
        transfer_id INT AUTO_INCREMENT PRIMARY KEY,
        evidence_id VARCHAR(255) NOT NULL,
        transferred_by_badge VARCHAR(50) NOT NULL,
        received_by_badge VARCHAR(50) NOT NULL,
        reason VARCHAR(255) NOT NULL,
        transfer_time DATETIME NOT NULL,
        previous_hash VARCHAR(255) NOT NULL,
        current_hash VARCHAR(255) NOT NULL,
        FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id),
        FOREIGN KEY (transferred_by_badge) REFERENCES personnel(badge_number),
        FOREIGN KEY (received_by_badge) REFERENCES personnel(badge_number)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lab_analysis (
        request_id INT AUTO_INCREMENT PRIMARY KEY,
        evidence_id VARCHAR(255) NOT NULL,
        requested_by_badge VARCHAR(50) NOT NULL,
        test_type VARCHAR(100) NOT NULL,
        request_date DATETIME NOT NULL,
        status VARCHAR(50) DEFAULT 'Pending',
        result_summary TEXT,
        report_file_path VARCHAR(500),
        equipment_used VARCHAR(255),
        completed_at DATETIME,
        FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id),
        FOREIGN KEY (requested_by_badge) REFERENCES personnel(badge_number)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS temperature_logs (
        log_id INT AUTO_INCREMENT PRIMARY KEY,
        location_id VARCHAR(100) NOT NULL,
        recorded_at DATETIME NOT NULL,
        temperature_celsius DECIMAL(5,2) NOT NULL,
        alert_triggered BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (location_id) REFERENCES storage_locations(location_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS legal_dispositions (
        disposition_id INT AUTO_INCREMENT PRIMARY KEY,
        evidence_id VARCHAR(255) NOT NULL,
        action_type VARCHAR(100) NOT NULL,
        authorized_by_badge VARCHAR(50) NOT NULL,
        action_date DATETIME NOT NULL,
        witnessed_by_badge VARCHAR(50),
        court_order_reference VARCHAR(255),
        FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id),
        FOREIGN KEY (authorized_by_badge) REFERENCES personnel(badge_number),
        FOREIGN KEY (witnessed_by_badge) REFERENCES personnel(badge_number)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_audit_logs (
        audit_id INT AUTO_INCREMENT PRIMARY KEY,
        evidence_id VARCHAR(255) NOT NULL, -- Added NOT NULL for stricter integrity
        result_message TEXT,
        status VARCHAR(50), -- 'Pass' or 'Fail'
        audit_time DATETIME,
        FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id)
    )
    """)

    conn.commit()
    conn.close()
    print("Complete MySQL Forensic Schema initialized successfully!")


if __name__ == "__main__":
    initialize_database()
