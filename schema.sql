-- Database Schema for Dermatologist Clinic Management & Prescription System

PRAGMA foreign_keys = ON;

-- Settings table for Clinic metadata
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Medicines table
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    default_dosage TEXT,
    default_frequency TEXT,
    default_duration TEXT,
    urdu_instructions TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prescriptions table
CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    doctor_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Prescription items table (linking medications to prescriptions)
CREATE TABLE IF NOT EXISTS prescription_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id INTEGER NOT NULL,
    medicine_id INTEGER,
    medicine_name TEXT NOT NULL,
    dosage TEXT,
    frequency TEXT,
    duration TEXT,
    urdu_instructions TEXT,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone);
CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(name);
CREATE INDEX IF NOT EXISTS idx_medicines_name ON medicines(name);
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_id);

-- Insert Default Settings
INSERT OR IGNORE INTO settings (key, value) VALUES 
('doctor_name', 'Dr. Sarah Ahmed'),
('doctor_specialty', 'MBBS, MD (Dermatology), FCPS - Skin & Hair Specialist'),
('clinic_name', 'DermaCare Skin & Laser Clinic'),
('clinic_phone', '+92 300 1234567'),
('clinic_address', 'Suite 101, Medical Plaza, Sector G, Phase 5, DHA, Lahore');

-- Insert Initial Medicines Seed Data
INSERT OR IGNORE INTO medicines (name, category, default_dosage, default_frequency, default_duration, urdu_instructions, notes) VALUES
('Cetirizine 10mg Tablet', 'Oral Antihistamine', '1 Tablet', 'Once Daily (Night)', '5 Days', 'یہ دوا روزانہ ایک گولی رات کو سوتے وقت استعمال کریں۔', 'For allergy and itching.'),
('Fexofenadine 120mg Tablet', 'Oral Antihistamine', '1 Tablet', 'Once Daily (Morning)', '10 Days', 'یہ گولی روزانہ صبح ناشتے کے بعد پانی کے ساتھ لیں۔', 'Non-drowsy antihistamine.'),
('Clotrimazole 1% Cream', 'Topical Antifungal', 'Apply thinly', 'Twice Daily', '2 Weeks', 'متاثرہ حصے کو دھونے اور خشک کرنے کے بعد کریم صبح اور شام ہلکے ہاتھ سے لگائیں۔', 'For fungal infections (ringworm, tinea).'),
('Hydrocortisone 1% Cream', 'Topical Steroid', 'Apply thinly', 'Twice Daily', '7 Days', 'خارش یا سوزش والے حصے پر کریم صبح اور شام ہلکے ہاتھ سے لگائیں۔ ۷ دن سے زیادہ استعمال نہ کریں۔', 'Mild steroid cream for eczema or contact dermatitis.'),
('Doxycycline 100mg Capsule', 'Oral Antibiotic', '1 Capsule', 'Twice Daily', '14 Days', 'ایک کیپسول صبح اور ایک شام کھانے کے بعد پانی کے بڑے گلاس کے ساتھ لیں۔ دوا لینے کے فوراً بعد لیٹیں نہیں۔', 'For moderate to severe acne or bacterial infections.'),
('Minoxidil 5% Topical Solution', 'Hair Growth Stimulant', '1 ml (8 sprays)', 'Twice Daily', '3 Months', 'صبح اور شام سر کے متاثرہ حصے (جہاں بال کم ہوں) پر 1 ملی لیٹر (8 سپرے) لگا کر ہلکا مساج کریں۔', 'For androgenetic alopecia (pattern hair loss).'),
('Permethrin 5% Cream', 'Topical Scabicide', 'Apply body-wide', 'Once (Repeat in 7 days if needed)', '8-14 Hours', 'گردن سے لے کر پاؤں کے ناخنوں تک پورے جسم پر لگائیں۔ ۸ سے ۱۴ گھنٹے بعد دھو لیں۔', 'For scabies treatment.'),
('Salicylic Acid 2% Gel', 'Keratolytic / Acne Care', 'Apply to acne spots', 'Once Daily (Night)', '4 Weeks', 'روزانہ رات کو چہرہ دھونے کے بعد صرف دانوں پر لگائیں۔', 'For acne spots and blackheads.');
