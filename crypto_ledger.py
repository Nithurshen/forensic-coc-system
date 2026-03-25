import hashlib
import json
import db_manager

def generate_row_hash(payload_dict):
    """
    Takes a transfer dictionary, sorts the keys to ensure consistent 
    JSON string formatting, and generates a SHA-256 hash.
    """
    hash_data = payload_dict.copy()
    
    if 'current_hash' in hash_data:
        del hash_data['current_hash']
        
    row_string = json.dumps(hash_data, sort_keys=True)
    
    return hashlib.sha256(row_string.encode('utf-8')).hexdigest()

def process_new_transfer(transfer_payload):
    """
    The master function to process a new transfer. 
    It fetches the old hash, generates the new one, and saves it to the DB.
    """
    evidence_id = transfer_payload['evidence_id']
    
    previous_hash = db_manager.get_latest_hash(evidence_id)
    transfer_payload['previous_hash'] = previous_hash
    
    current_hash = generate_row_hash(transfer_payload)
    transfer_payload['current_hash'] = current_hash
    
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
    with db_manager.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM chain_of_custody 
            WHERE evidence_id = ? 
            ORDER BY transfer_id ASC
        ''', (evidence_id,))
        records = [dict(row) for row in cursor.fetchall()]
        
    if not records:
        return False, "No records found for this evidence ID."

    expected_previous = "GENESIS_HASH"
    
    for row in records:
        if row['previous_hash'] != expected_previous:
            return False, f"Integrity Failure: Broken chain at Transfer ID {row['transfer_id']}"
            
        recalculated_hash = generate_row_hash(row)
        
        if recalculated_hash != row['current_hash']:
            return False, f"Tampering Detected: Hash mismatch at Transfer ID {row['transfer_id']}"

        expected_previous = recalculated_hash
        
    return True, "Ledger is mathematically intact. All hashes verified."