# Forensic Evidence & Chain of Custody System

This project is a high-integrity, cryptographically secured **Forensic Evidence Management System**. Designed for law enforcement and forensic laboratories, it tracks physical, biological, and digital evidence from the moment of intake through its entire legal lifecycle. 

By utilizing a linked-ledger architecture (similar to a blockchain) and SHA-256 hashing, the system ensures that the **Chain of Custody (CoC)** remains completely immutable and tamper-evident, strictly adhering to the rigorous standards required for court-admissible reporting.

## 🚀 Comprehensive Feature Set

### 🔐 Security & Access Control
* **Encrypted Authentication:** Role-based access control using `bcrypt` password hashing for forensic officers, lab technicians, and investigators.
* **Department & Clearance Tracking:** Associates personnel with specific departments (Homicide, Lab Tech, Evidence Control) and tracks clearance levels.

### 📦 Evidence Intake & Digital Fingerprinting
* **Multi-Type Evidence Logging:** Supports structured intake for Physical, Biological, and Digital evidence.
* **Genesis Hashing:** Automatically generates a secure SHA-256 hash for uploaded digital items (CCTV footage, disk images, PDFs) at the exact moment of intake to mathematically prove the file's original state.
* **Automated Genesis Block:** The initial logging instantly creates a cryptographically sealed "Genesis Transfer" in the ledger.

### 🔗 Immutable Chain of Custody (The Cryptographic Ledger)
* **Linked-Hash Architecture:** Every transfer of custody mathematically incorporates the previous record's hash, creating an unbreakable chain. If any historical database row is altered, the subsequent hashes will fail to validate.
* **Comprehensive Transfer Logs:** Records the exact timestamp, relinquishing officer, receiving officer, and the specific reason for transfer (e.g., Transport to Lab, Court Appearance).

### 🛡️ System Auditing & Verification
* **Court-Level Ledger Audit:** Recalculates the entire hash chain for a specific piece of evidence from its genesis to its current state, proving zero database tampering.
* **Global System Integrity Check:** Scans the entire MySQL database, validating the cryptographic chains of *every* piece of evidence simultaneously.
* **Digital Integrity Verification:** Allows investigators to upload a local file and instantly verify its hash against the court-recorded value in the database to detect corruption or manipulation.
* **Automated PDF Reporting:** Generates downloadable, court-ready PDF Chain of Custody reports detailing the complete timeline, officer identities, and cryptographic signatures.

### 📂 Case & Investigation Management
* **Case Creation:** Open and track cases with assigned lead investigators and status monitoring (Open, Under Review, Closed).
* **Case Updating:** Modify existing case statuses and reassign lead investigators as investigations progress.
* **Many-to-Many Evidence Linking:** Link a single piece of evidence to multiple cases or multiple pieces of evidence to a single case using a relational junction mapping.
* **Cross-Referencing View:** Instantly query a piece of evidence to view every active or closed case it is associated with.

### 🔬 Lab & Forensics Tracking
* **Analysis Queuing:** Submit specific lab requests (DNA Profiling, Ballistics, Toxicology, Digital Forensics) directly to the lab queue.
* **Result Logging:** Dynamically fetch currently pending requests to update with result summaries, equipment used (e.g., GC-MS Spectrometer), and file paths to network-stored forensic reports.

### 🌡️ Facility & Environmental Management
* **Dynamic Facility Registration:** Add new secure storage locations (e.g., Deep Freezers, Faraday Lockers, Vehicle Impounds, Biohazard Refrigerators).
* **Smart Temperature Logging:** Manually log environmental temperatures via a filtered interface that only displays locations explicitly requiring climate monitoring.
* **Automated Threshold Alerts:** System triggers visual warnings if recorded temperatures exceed safe limits for specific storage types (e.g., > -10.0°C for deep freezes).

### ⚖️ Legal Dispositions
* **Final Actions:** Record the legal end-of-life for evidence (Released to Owner, Destroyed/Incinerated, Transferred to Federal Custody).
* **Two-Officer Authorization:** Requires both an authorizing officer and a witnessing officer (mandatory for evidence destruction), alongside court order reference numbers.

### 📊 Real-Time Dashboard
* **System Overview Metrics:** Live counts on total cases, evidence logged, and pending lab requests.
* **Comprehensive Multi-Column View:** Simultaneously view actionable lists of Pending Lab Requests, the Full Evidence Registry, and All Cases directly on the home dashboard.
* **Searchable Registry:** Quickly locate evidence by ID or description.
* **"Needs Attention" Flagging:** Automatically highlights evidence currently sitting in insecure "Temporary Holding" or items that have failed a cryptographic integrity audit.

## 🛠️ Tech Stack

* **Frontend UI:** Streamlit (Python-based Web Framework)
* **Database:** MySQL (Relational storage mapped with strict Foreign Keys)
* **Security & Crypto:** `bcrypt` (Passwords), `hashlib` (SHA-256 Ledger & File Hashing)
* **Reporting:** `fpdf` (Automated PDF generation)
* **Environment Setup:** `python-dotenv`

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Nithurshen/forensic-coc-system.git
cd forensic-coc-system
```

### 2. Install Dependencies
Ensure you have Python 3.8+ installed, then install the required libraries:
```bash
pip install -r requirements.txt
```

### 3. Database Configuration
Ensure your MySQL server is running. Create a `.env` file in the root directory of the project and provide your credentials:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=forensic_db
SECRET_KEY=super_secure_random_salt_string
```

### 4. Initialize and Seed the System
Run the initialization script. **Note: This will drop existing tables and start fresh.** It builds the relational schema and seeds the default storage facilities.
```bash
python reset_system.py
```

### 5. Launch the Application
Start the secure Streamlit web interface:
```bash
streamlit run app.py
```

## 📚 References & Resources

This project was built using the following tools and libraries. We referred to their official documentation during development:

* **Streamlit Documentation (Frontend Framework):** [https://docs.streamlit.io/](https://docs.streamlit.io/)
* **MySQL Python Connector Official Guide:** [https://dev.mysql.com/doc/connector-python/en/](https://dev.mysql.com/doc/connector-python/en/)
* **Python hashlib (SHA-256 Cryptography):** [https://docs.python.org/3/library/hashlib.html](https://docs.python.org/3/library/hashlib.html)
* **FPDF Library (Automated Reporting):** [https://pyfpdf.readthedocs.io/](https://pyfpdf.readthedocs.io/)
* **Bcrypt Library (Password Hashing):** [https://pypi.org/project/bcrypt/](https://pypi.org/project/bcrypt/)

## 📄 License

This project is licensed under the **Apache License 2.0**. You may not use this file except in compliance with the License. You may obtain a copy of the License at `http://www.apache.org/licenses/LICENSE-2.0`. See the `LICENSE` file for the specific language governing permissions and limitations.
