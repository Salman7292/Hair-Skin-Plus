# Hair Skin Plus — Digital Prescription & Clinic Management System

**Dr. Seyab Ur Rahman**  
*MBBS (PAK), FCPS (Dermatology) • Fellowship Paeds Dermatology*  
*Consultant Dermatologist &bull; Ex Registrar CMH Peshawar*  
*New Samad Building, Dabgari Garden, Peshawar*

---

A modern, offline-capable, and comprehensive Clinic Management & Digital Prescription System designed specifically for dermatology practices. Built with Python (Flask) on the backend, SQLite for local data persistence, and Tailwind CSS with Vanilla JavaScript on the frontend.

---

## 🌟 Key Features

- **Full-Window Welcome Screen**:
  - Immersive doctor welcome dashboard with quick-action cards for consultation desk, medicine catalog, patient records, and intake.
- **Prescription Desk & Live Preview**:
  - Split-pane interface allowing real-time clinical note taking, complaint registration, and dynamic medicine prescribing with immediate visual card preview.
- **High-Fidelity Printable A4 Prescription Sheet**:
  - Luxury medical design with deep forest teal (`#0b5650`), warm amber gold (`#e0a030`), and soft mint accents.
  - Official clinic logo, doctor credentials, patient information grid, ruled clinical notes, investigation column, Rx table, and Urdu instructions in *Noto Nastaliq Urdu*.
  - Print-optimized CSS (`@media print`) configured strictly for standard A4 portrait pages with zero layout overflow.
- **Urdu Prescription Instructions (RTL)**:
  - Pre-seeded and customizable medication frequencies, durations, and advice rendered in beautiful Nastaliq typography.
- **Patient Management & Longitudinal History**:
  - Comprehensive intake registry, real-time returning patient search, and one-click **Repeat Last Rx** to instantly copy prior prescriptions.
- **Medicine Catalog**:
  - Searchable catalog of dermatological drugs with custom dosages, forms, and instructions.
- **100% Offline Capability**:
  - Bundled local fonts (*Libre Baskerville*, *Playfair Display*, *Poppins*, *Plus Jakarta Sans*) and precompiled standalone Tailwind CSS (`tailwind.min.css`) so the application functions seamlessly without an active internet connection.

---

## 🚀 Quick Start & Installation

### 1. Requirements
- Python 3.9+
- Flask

### 2. Setup & Installation
```powershell
# Clone the repository
git clone https://github.com/Salman7292/Hair-Skin-Plus.git
cd Hair-Skin-Plus

# Install required dependencies
pip install -r requirements.txt
```

### 3. Running the Application
```powershell
python app.py
```

The application runs locally at:  
👉 **[http://127.0.0.1:5050](http://127.0.0.1:5050)**

---

## 📂 Project Structure

```text
Hair-Skin-Plus/
│
├── app.py                  # Main Flask application and REST API endpoints
├── medicines.db            # SQLite database for patients, visits, and medicines
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation
│
├── static/
│   ├── css/
│   │   ├── style.css       # Core clinical theme, print rules, and layouts
│   │   ├── fonts.css       # Local self-hosted font definitions
│   │   └── tailwind.min.css# Standalone offline Tailwind bundle
│   ├── js/
│   │   ├── tailwind.cdn.js # Offline client-side Tailwind compiler
│   │   └── app.js          # Client-side helper routines
│   ├── fonts/              # Offline TTF / WOFF2 font files
│   ├── stamp.png           # Official clinic logo / seal
│   ├── signature.png       # Doctor digital signature
│   ├── doctor_photo.png    # Doctor portrait hero cutout
│   └── app_icon.ico        # Window and browser application icon
│
└── templates/
    └── index.html          # Single-page application template
```

---

## 📜 License
Private clinic management software for **Hair Skin Plus** — Dr. Seyab Ur Rahman.
