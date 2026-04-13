# Forensic Evidence & Chain of Custody System

This project is a high-integrity **Forensic Evidence Management System** designed to track physical and digital evidence from the moment of intake through its entire legal lifecycle. By utilizing cryptographic hashing and a linked-ledger architecture, the system ensures that the **Chain of Custody (CoC)** remains immutable and tamper-evident, meeting the rigorous standards required for court-admissible reporting.

## Key Features

* **Cryptographic Ledger**: Every transfer of custody is hashed and linked to the previous record, creating a mathematical "chain" that detects any unauthorized database tampering.
* **Digital Integrity Verification**: Allows investigators to upload digital files (CCTV, disk images) and verify their SHA-256 hashes against the original intake record.
* **Secure Authentication**: Role-based access control using `bcrypt` password hashing for forensic officers and lab technicians.
* **Automated Court Reporting**: Generates official PDF Chain of Custody reports containing timestamps, officer identities, and cryptographic signatures.
* **Facility Management**: Tracks evidence across various specialized environments, including biohazard refrigerators, Faraday lockers, and vehicle impounds.
* **Audit Dashboard**: Real-time overview of total cases, pending lab requests, and items requiring immediate attention (e.g., items in temporary holding).

## Tech Stack

* **Frontend**: Streamlit (Python-based Web UI)
* **Database**: MySQL (Relational storage for evidence, personnel, and logs)
* **Security**: `bcrypt` (password hashing), `hashlib` (SHA-256 for ledger integrity)
* **Reporting**: `fpdf` (PDF generation)
* **Environment**: `python-dotenv` for secure credential management

## Prerequisites

Before running the system, ensure you have the following installed:
* Python 3.8+
* MySQL Server
* A tool to manage Python environments (like `venv` or `conda`)

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd forensic-coc-system
```

### 2. Install Dependencies
Install the required libraries listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Database Configuration
Create a `.env` file in the root directory and provide your MySQL credentials:
```env
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=forensic_db
SECRET_KEY=your_secure_salt_string
```

### 4. Initialize and Seed the System
Run the reset script to create the database schema and populate initial storage locations (Freezers, Vaults, etc.):
```bash
python reset_system.py
```

## Usage Guide

### 1. Launch the Application
Start the Streamlit web interface:
```bash
streamlit run app.py
```

### 2. User Registration & Login
* **Register**: Navigate to the "Register Officer" tab to create your account.
* **Login**: Use your credentials to access the secure dashboard.

### 3. Logging New Evidence
* Go to **Log New Evidence**.
* Enter the Evidence ID and description.
* If the evidence is digital, upload the file to generate its "Genesis Hash."
* Assign a storage location (e.g., "LOC-F1 Deep Freezer").

### 4. Performing a Transfer
* Select **Transfer Custody**.
* Identify the item and the personnel involved.
* Once submitted, the system automatically links the new transfer to the previous hash, sealing the record.

### 5. Auditing for Court
* Select **Audit & Verify Ledger**.
* Enter an Evidence ID to trigger a full cryptographic audit.
* If the chain is intact, click **Download Court Report (PDF)** to generate the official documentation.

## License
This project is licensed under the **Apache License 2.0**. You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0). See the `LICENSE` file for details on permissions and limitations.