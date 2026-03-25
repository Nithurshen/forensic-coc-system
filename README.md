# Forensic Evidence & Chain of Custody System (forensic-coc-system)

A high-security database system designed for crime laboratories and police departments to manage the collection, analysis, storage, and court presentation of forensic evidence. 

Unlike standard inventory applications, this system replaces traditional state changes with strict "transfers of custody" and prioritizes absolute data integrity. Evidence records are immutable, and every transfer is permanently recorded in a mathematically verifiable ledger to ensure strict court admissibility.

## The Core Innovation: Cryptographic Row-Linking

Standard SQL audit tables are vulnerable to manipulation by actors with database-level access. To mitigate this risk, `forensic-coc-system` implements a Tamper-Evident SQL Ledger directly within the relational database, avoiding the computational overhead of external blockchain infrastructure.

Every transfer of custody generates a `CurrentHash` alongside a `PreviousHash`. When a new transfer occurs, the system calculates a SHA-256 hash combining the new transaction payload with the hash of the preceding transaction for that specific item. 

> **Result:** If any historical record (such as a timestamp or location) is manually altered at the database level, the subsequent mathematical chain is instantly invalidated. The built-in ledger verification tool recalculates these hashes in real-time, providing cryptographic proof of database integrity for legal scrutiny.

## Technical Stack

* **Frontend:** Streamlit (Python) for rapid deployment and state management.
* **Backend Logic:** Python (`hashlib` for cryptography, `pandas` for data structuring).
* **Database:** SQL (SQLite for initial development and prototyping; architected for migration to PostgreSQL in production environments).

## Architecture & Division of Labor

This project utilizes a decoupled architecture to facilitate parallel development across a four-person team:

* **Database Administration (DBA):** Manages the relational SQL schema, enforces foreign key constraints, and optimizes query execution.
* **Backend Cryptography:** Develops the SHA-256 hashing logic, manages digital evidence hashing, and maintains the ledger verification loops.
* **Frontend Architecture:** Constructs the Streamlit interface, user workflows, and secure data-entry forms.
* **System Integration:** Connects backend cryptographic states to the frontend UI and orchestrates automated, court-compliant reporting mechanisms.

## Key System Features

* **Evidence Intake & Cataloging:** Secure logging of physical and biological items with precise metadata (GPS coordinates, collection personnel, environmental parameters).
* **Immutable Chain of Custody:** Continuous, append-only tracking of item possession, including authorized personnel, timestamps, and transfer rationales.
* **Laboratory Analysis Tracking:** Relational linking of evidence items to analysis requests, analytical reports (e.g., toxicology), and equipment calibration logs.
* **Secure Storage Management:** Granular inventory control mapping items to specific shelves, bins, or temperature-controlled freezer units.
* **Automated Court Reporting:** Generation of formatted, continuously linked Chain of Custody timelines designed specifically for legal proceedings.

## Getting Started (Development Setup)

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-org/forensic-coc-system.git](https://github.com/your-org/forensic-coc-system.git)
   cd forensic-coc-system
   ```

2. **Initialize a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the local database:**
   ```bash
   python scripts/init_db.py
   ```

5. **Launch the application:**
   ```bash
   streamlit run app.py
   ```

## Security Note

This architecture relies heavily on cryptographic hashing for data verification. Ensure that all database connection strings, secret keys, and environment variables are strictly isolated and secured before deploying to any staging or production environments. Do not commit `.env` files to version control.