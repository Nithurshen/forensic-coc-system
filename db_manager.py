import mysql.connector

def get_db_connection():
    """Establish connection to the MySQL server."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",
        database="forensics_coc"
    )

def get_latest_hash(evidence_id):
    """Fetches the CurrentHash of the most recent transfer for a specific item."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT current_hash 
        FROM chain_of_custody 
        WHERE evidence_id = %s 
        ORDER BY transfer_id DESC 
        LIMIT 1
    ''', (evidence_id,))
    result = cursor.fetchone()
    
    conn.close()
    return result['current_hash'] if result else "GENESIS_HASH"

def insert_transfer(payload):
    """Inserts a newly hashed transfer payload into the MySQL database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO chain_of_custody (
                evidence_id, transferred_by_badge, received_by_badge, 
                reason, transfer_time, previous_hash, current_hash
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            payload['evidence_id'], payload['transferred_by_badge'], 
            payload['received_by_badge'], payload['reason'], 
            payload['transfer_time'], payload['previous_hash'], 
            payload['current_hash']
        ))
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
        cursor.execute('''
            INSERT INTO personnel (badge_number, first_name, last_name, department, clearance_level)
            VALUES (%s, %s, %s, %s, %s)
        ''', (badge, first, last, dept, clearance))
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