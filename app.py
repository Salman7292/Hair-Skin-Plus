import os
import re
import sqlite3
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g

app = Flask(__name__)
app.secret_key = 'derma_medicine_catalog_key'

DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'medicines.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/api/client_error', methods=['POST'])
def log_client_error():
    data = request.get_json(silent=True) or {}
    print(f"\n[CLIENT JAVASCRIPT ERROR] Line {data.get('line')}:{data.get('col')} -> {data.get('message')}\nStack: {data.get('stack')}\n", flush=True)
    return jsonify({"status": "received"})

# ── Normalization & Identification Utilities ─────────────────────────────────

def clean_phone(phone):
    """Normalize phone number to raw comparable digits."""
    if not phone:
        return ''
    digits = re.sub(r'\D', '', str(phone))
    if digits.startswith('0092') and len(digits) >= 14:
        digits = '0' + digits[4:]
    elif digits.startswith('92') and len(digits) >= 12:
        digits = '0' + digits[2:]
    return digits

def clean_name(name):
    """Normalize patient name for case-insensitive, whitespace-insensitive matching."""
    if not name:
        return ''
    return ' '.join(str(name).strip().lower().split())

def generate_patient_id(numeric_id):
    """Generate uniform clinical Patient ID format: HSP-0001."""
    return f"HSP-{int(numeric_id):04d}"

def merge_duplicate_patients(db):
    """Scan and merge duplicate patient profiles in the database if any exist."""
    if not db.row_factory:
        db.row_factory = sqlite3.Row
    all_patients = db.execute("SELECT id, name, phone, age, gender, created_at FROM patients ORDER BY id ASC").fetchall()
    
    seen_canonical = {}  # key -> primary_patient_id
    for p in all_patients:
        p_id = p['id']
        p_phone = clean_phone(p['phone'])
        p_name = clean_name(p['name'])
        
        # Primary lookup key: phone if valid (>= 7 digits), else normalized name
        key = f"phone:{p_phone}" if len(p_phone) >= 7 else f"name:{p_name}"
        
        if key in seen_canonical:
            primary_id = seen_canonical[key]
            # Re-link any consultations to the primary patient
            db.execute("UPDATE prescriptions SET patient_id = ? WHERE patient_id = ?", (primary_id, p_id))
            # Delete the duplicate patient row
            db.execute("DELETE FROM patients WHERE id = ?", (p_id,))
        else:
            seen_canonical[key] = p_id

    db.commit()

# ── Database Initialization & Safe Column Migrations ─────────────────────────

def init_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL DEFAULT '',
            default_dosage TEXT DEFAULT '',
            default_frequency TEXT DEFAULT '',
            default_duration TEXT DEFAULT '',
            urdu_instructions TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            name TEXT NOT NULL,
            phone TEXT DEFAULT '',
            age TEXT DEFAULT '',
            gender TEXT DEFAULT '',
            address TEXT DEFAULT '',
            allergies TEXT DEFAULT '',
            medical_history TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            patient_name TEXT NOT NULL,
            patient_phone TEXT DEFAULT '',
            patient_age TEXT DEFAULT '',
            patient_gender TEXT DEFAULT '',
            visit_number INTEGER DEFAULT 1,
            complaints TEXT DEFAULT '',
            examination TEXT DEFAULT '',
            diagnosis TEXT DEFAULT '',
            treatment_plan TEXT DEFAULT '',
            follow_up TEXT DEFAULT '',
            doctor_notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS prescription_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prescription_id INTEGER NOT NULL,
            medicine_name TEXT NOT NULL,
            dosage TEXT DEFAULT '',
            frequency TEXT DEFAULT '',
            duration TEXT DEFAULT '',
            urdu_instructions TEXT DEFAULT '',
            FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(name);
        CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone);
        CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_id);
        CREATE INDEX IF NOT EXISTS idx_prescription_items_rx ON prescription_items(prescription_id);

        INSERT OR IGNORE INTO medicines
            (name, category, default_dosage, default_frequency, default_duration, urdu_instructions, notes)
        VALUES
        ('Cetirizine 10mg Tablet',      'Oral Antihistamine',    '1 Tablet',       'Once Daily (Night)', '5 Days',   'یہ دوا روزانہ ایک گولی رات کو سوتے وقت استعمال کریں۔',                       'For allergy and itching.'),
        ('Fexofenadine 120mg Tablet',   'Oral Antihistamine',    '1 Tablet',       'Once Daily (Morning)','10 Days', 'یہ گولی روزانہ صبح ناشتے کے بعد پانی کے ساتھ لیں۔',                          'Non-drowsy antihistamine.'),
        ('Clotrimazole 1% Cream',       'Topical Antifungal',    'Apply thinly',   'Twice Daily',         '2 Weeks', 'متاثرہ حصے کو دھو کر خشک کریں پھر صبح اور شام کریم لگائیں۔',               'For fungal infections.'),
        ('Hydrocortisone 1% Cream',     'Topical Steroid',       'Apply thinly',   'Twice Daily',         '7 Days',  'خارش یا سوزش والے حصے پر صبح اور شام ہلکے ہاتھ سے لگائیں۔',               'Mild steroid cream.'),
        ('Doxycycline 100mg Capsule',   'Oral Antibiotic',       '1 Capsule',      'Twice Daily',         '14 Days', 'ایک کیپسول صبح اور ایک شام کھانے کے بعد پانی کے ساتھ لیں۔',                'For moderate to severe acne.'),
        ('Minoxidil 5% Solution',       'Hair Growth Stimulant', '1 ml',           'Twice Daily',         '3 Months','صبح اور شام سر کے متاثرہ حصے پر ایک ملی لیٹر لگا کر ہلکا مساج کریں۔',    'For androgenetic alopecia.'),
        ('Permethrin 5% Cream',         'Topical Scabicide',     'Apply body-wide','Once',                '8-14 Hrs','گردن سے پاؤں تک پورے جسم پر لگائیں، ۸ گھنٹے بعد دھو لیں۔',               'For scabies treatment.'),
        ('Salicylic Acid 2% Gel',       'Keratolytic/Acne',      'Apply to spots', 'Once Daily (Night)',  '4 Weeks', 'رات کو چہرہ دھونے کے بعد صرف دانوں پر لگائیں۔',                            'For acne spots and blackheads.'),
        ('Betamethasone 0.1% Cream',    'Topical Steroid',       'Apply thinly',   'Twice Daily',         '10 Days', 'متاثرہ جگہ پر دن میں دو بار ہلکے ہاتھ سے لگائیں، ۱۰ دن سے زیادہ نہ لگائیں۔','Potent steroid - short-term use only.'),
        ('Mupirocin 2% Ointment',       'Topical Antibiotic',    'Apply to wound', 'Three Times Daily',   '5 Days',  'متاثرہ جگہ کو صاف کر کے دن میں تین بار مرہم لگائیں۔',                    'For impetigo and infected wounds.');
    """)

    # Column migrations to gracefully preserve existing databases
    def ensure_column(table, column, col_def):
        existing_cols = [row['name'] for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in existing_cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")

    ensure_column("patients", "patient_id", "TEXT")
    ensure_column("patients", "address", "TEXT DEFAULT ''")
    ensure_column("patients", "allergies", "TEXT DEFAULT ''")
    ensure_column("patients", "medical_history", "TEXT DEFAULT ''")

    ensure_column("prescriptions", "visit_number", "INTEGER DEFAULT 1")
    ensure_column("prescriptions", "complaints", "TEXT DEFAULT ''")
    ensure_column("prescriptions", "examination", "TEXT DEFAULT ''")
    ensure_column("prescriptions", "treatment_plan", "TEXT DEFAULT ''")
    ensure_column("prescriptions", "follow_up", "TEXT DEFAULT ''")

    # Generate patient_id for any existing patient lacking one
    rows = cursor.execute("SELECT id, patient_id FROM patients").fetchall()
    for r in rows:
        if not r['patient_id']:
            gen_id = generate_patient_id(r['id'])
            cursor.execute("UPDATE patients SET patient_id = ? WHERE id = ?", (gen_id, r['id']))

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON patients(patient_id)")

    # Compute visit_number for any existing prescriptions
    p_rows = cursor.execute("SELECT id, patient_id FROM prescriptions ORDER BY datetime(created_at) ASC, id ASC").fetchall()
    counters = {}
    for pr in p_rows:
        pid = pr['patient_id']
        counters[pid] = counters.get(pid, 0) + 1
        cursor.execute("UPDATE prescriptions SET visit_number = ? WHERE id = ?", (counters[pid], pr['id']))

    db.commit()
    merge_duplicate_patients(db)
    db.close()

# ── Web Application Route: Main Workspace ────────────────────────────────────

@app.route('/')
def index():
    db = get_db()
    q = request.args.get('q', '').strip()
    if q:
        rows = db.execute(
            "SELECT * FROM medicines WHERE name LIKE ? OR category LIKE ? ORDER BY name",
            (f'%{q}%', f'%{q}%')
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM medicines ORDER BY name").fetchall()
    medicines = [dict(r) for r in rows]

    # Clinical Statistics
    patient_count = db.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    rx_count = db.execute("SELECT COUNT(*) FROM prescriptions").fetchone()[0]
    medicines_count = len(medicines)
    
    # Consultations today
    today_str = date.today().isoformat()
    today_rx_count = db.execute(
        "SELECT COUNT(*) FROM prescriptions WHERE date(created_at) = ?",
        (today_str,)
    ).fetchone()[0]

    return render_template(
        'index.html',
        medicines=medicines,
        q=q,
        patient_count=patient_count,
        rx_count=rx_count,
        medicines_count=medicines_count,
        today_rx_count=today_rx_count
    )

# ── Medicine Catalog Management Routes ───────────────────────────────────────

@app.route('/add', methods=['POST'])
def add_medicine():
    data = _extract_med_form()
    if not data['name']:
        flash('Medicine name is required.', 'error')
        return redirect(url_for('index'))
    try:
        get_db().execute(
            """INSERT INTO medicines (name,category,default_dosage,default_frequency,
               default_duration,urdu_instructions,notes) VALUES (?,?,?,?,?,?,?)""",
            (data['name'], data['category'], data['default_dosage'],
             data['default_frequency'], data['default_duration'],
             data['urdu_instructions'], data['notes'])
        )
        get_db().commit()
        flash(f'"{data["name"]}" added to catalog.', 'success')
    except sqlite3.IntegrityError:
        flash('A medicine with that name already exists.', 'error')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_medicine(id):
    data = _extract_med_form()
    if not data['name']:
        flash('Medicine name is required.', 'error')
        return redirect(url_for('index'))
    try:
        get_db().execute(
            """UPDATE medicines SET name=?,category=?,default_dosage=?,default_frequency=?,
               default_duration=?,urdu_instructions=?,notes=? WHERE id=?""",
            (data['name'], data['category'], data['default_dosage'],
             data['default_frequency'], data['default_duration'],
             data['urdu_instructions'], data['notes'], id)
        )
        get_db().commit()
        flash(f'"{data["name"]}" updated.', 'success')
    except sqlite3.IntegrityError:
        flash('A medicine with that name already exists.', 'error')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_medicine(id):
    row = get_db().execute("SELECT name FROM medicines WHERE id=?", (id,)).fetchone()
    if row:
        get_db().execute("DELETE FROM medicines WHERE id=?", (id,))
        get_db().commit()
        flash(f'"{row["name"]}" deleted.', 'success')
    return redirect(url_for('index'))

@app.route('/api/medicine/<int:id>')
def api_get_medicine(id):
    row = get_db().execute("SELECT * FROM medicines WHERE id=?", (id,)).fetchone()
    if row:
        return jsonify(dict(row))
    return jsonify({}), 404

# ── Patient Records & Medical Directory APIs ─────────────────────────────────

@app.route('/api/patients')
def api_get_all_patients():
    """
    Retrieve master directory of all registered patients with total visits,
    first and last visit timestamps, and latest diagnosis.
    Supports filtering by search query (name, ID, phone, diagnosis) and gender.
    """
    db = get_db()
    q = request.args.get('q', '').strip()
    gender = request.args.get('gender', '').strip()

    sql = """
        SELECT p.id, p.patient_id, p.name, p.phone, p.age, p.gender, p.address,
               p.allergies, p.medical_history, p.notes, p.created_at, p.updated_at,
               COUNT(pr.id) as visit_count,
               MIN(pr.created_at) as first_visit,
               MAX(pr.created_at) as last_visit,
               (SELECT diagnosis FROM prescriptions WHERE patient_id = p.id ORDER BY datetime(created_at) DESC, id DESC LIMIT 1) as latest_diagnosis,
               (SELECT GROUP_CONCAT(pi.medicine_name, ', ') 
                FROM prescription_items pi 
                WHERE pi.prescription_id = (SELECT id FROM prescriptions WHERE patient_id = p.id ORDER BY datetime(created_at) DESC, id DESC LIMIT 1)
               ) as latest_medicines_preview
        FROM patients p
        LEFT JOIN prescriptions pr ON p.id = pr.patient_id
    """
    params = []
    where_clauses = []

    if q:
        like = f"%{q}%"
        norm_p = clean_phone(q)
        if norm_p and len(norm_p) >= 4:
            where_clauses.append("(p.name LIKE ? OR p.patient_id LIKE ? OR p.phone LIKE ? OR p.phone LIKE ? OR pr.diagnosis LIKE ?)")
            params.extend([like, like, like, f"%{norm_p}%", like])
        else:
            where_clauses.append("(p.name LIKE ? OR p.patient_id LIKE ? OR p.phone LIKE ? OR pr.diagnosis LIKE ?)")
            params.extend([like, like, like, like])

    if gender:
        where_clauses.append("LOWER(p.gender) = LOWER(?)")
        params.append(gender)

    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    sql += " GROUP BY p.id ORDER BY p.updated_at DESC, p.id DESC"

    rows = db.execute(sql, params).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/patients/<int:patient_id>')
def api_get_patient_details(patient_id):
    """
    Retrieve complete patient medical profile and their entire chronological
    history of visits, clinical findings, diagnoses, and prescription sheets.
    """
    db = get_db()
    patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    # Fetch all consultations for this patient ordered chronologically (newest first)
    rx_rows = db.execute("""
        SELECT * FROM prescriptions 
        WHERE patient_id = ? 
        ORDER BY datetime(created_at) DESC, id DESC
    """, (patient_id,)).fetchall()

    history = []
    diagnoses_seen = set()
    for rx in rx_rows:
        rx_dict = dict(rx)
        if rx['diagnosis']:
            diagnoses_seen.add(rx['diagnosis'].strip())
        items = db.execute("""
            SELECT * FROM prescription_items 
            WHERE prescription_id = ? 
            ORDER BY id ASC
        """, (rx['id'],)).fetchall()
        rx_dict['items'] = [dict(it) for it in items]
        history.append(rx_dict)

    patient_dict = dict(patient)
    if not patient_dict.get('patient_id'):
        patient_dict['patient_id'] = generate_patient_id(patient_id)

    return jsonify({
        'patient': patient_dict,
        'history': history,
        'visits': history,
        'recurring_conditions': list(diagnoses_seen),
        'total_visits': len(history)
    })

@app.route('/api/patients', methods=['POST'])
def api_save_patient_profile():
    """Register a new patient or update demographic details."""
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Patient Name is required.'}), 400

    phone = data.get('phone', '').strip()
    age = data.get('age', '').strip()
    gender = data.get('gender', '').strip()
    address = data.get('address', '').strip()
    allergies = data.get('allergies', '').strip()
    medical_history = data.get('medical_history', '').strip()
    notes = data.get('notes', '').strip()
    patient_id = data.get('id')

    db = get_db()

    if patient_id:
        db.execute("""
            UPDATE patients 
            SET name = ?, phone = ?, age = ?, gender = ?, address = ?,
                allergies = ?, medical_history = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (name, phone, age, gender, address, allergies, medical_history, notes, patient_id))
        db.commit()
        return jsonify({'success': True, 'patient_id': patient_id, 'message': 'Patient profile updated.'})
    else:
        # Check if already exists by phone or name
        norm_phone = clean_phone(phone)
        matched = None
        if norm_phone and len(norm_phone) >= 7:
            for p in db.execute("SELECT id FROM patients WHERE phone != ''").fetchall():
                if clean_phone(p['phone']) == norm_phone:
                    matched = p
                    break

        if matched:
            p_id = matched['id']
            db.execute("""
                UPDATE patients 
                SET name = ?, phone = ?, age = ?, gender = ?, address = ?,
                    allergies = ?, medical_history = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (name, phone, age, gender, address, allergies, medical_history, p_id))
            db.commit()
            return jsonify({'success': True, 'patient_id': p_id, 'is_existing': True, 'message': 'Existing patient profile updated.'})

        cur = db.execute("""
            INSERT INTO patients (name, phone, age, gender, address, allergies, medical_history, notes, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (name, phone, age, gender, address, allergies, medical_history, notes))
        new_id = cur.lastrowid
        patient_code = generate_patient_id(new_id)
        db.execute("UPDATE patients SET patient_id = ? WHERE id = ?", (patient_code, new_id))
        db.commit()
        return jsonify({'success': True, 'patient_id': new_id, 'patient_code': patient_code, 'message': 'New patient registered.'})

# ── Patient Intake & Instant Lookup API ──────────────────────────────────────

@app.route('/api/patients/lookup')
def api_patient_lookup():
    """
    Instant clinical search for Patient Intake to verify if patient is present in history.
    Searches by Patient ID (e.g. HSP-0002), Phone number (clean), or Full Name.
    """
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'found': False, 'patient': None, 'history': []})

    db = get_db()
    norm_phone = clean_phone(q)
    norm_name = clean_name(q)
    clean_q = q.upper().replace(' ', '')

    matched = None

    # 1. Match by Patient ID (e.g. HSP-0002 or 0002)
    all_patients = db.execute("SELECT * FROM patients ORDER BY id ASC").fetchall()
    for p in all_patients:
        p_code = (p['patient_id'] or '').upper()
        if p_code and (clean_q == p_code or clean_q in p_code):
            matched = p
            break

    # 2. Match by clean phone number
    if not matched and norm_phone and len(norm_phone) >= 6:
        for p in all_patients:
            p_phone = clean_phone(p['phone'])
            if p_phone and (p_phone == norm_phone or p_phone.endswith(norm_phone) or norm_phone.endswith(p_phone)):
                matched = p
                break

    # 3. Match by normalized patient name
    if not matched and norm_name:
        for p in all_patients:
            if clean_name(p['name']) == norm_name:
                matched = p
                break

    if matched:
        patient_id = matched['id']
        rx_rows = db.execute("""
            SELECT * FROM prescriptions 
            WHERE patient_id = ? 
            ORDER BY datetime(created_at) DESC, id DESC
        """, (patient_id,)).fetchall()

        history = []
        diagnoses_set = set()
        for rx in rx_rows:
            rx_dict = dict(rx)
            if rx['diagnosis']:
                diagnoses_set.add(rx['diagnosis'].strip())
            items = db.execute("""
                SELECT * FROM prescription_items 
                WHERE prescription_id = ? 
                ORDER BY id ASC
            """, (rx['id'],)).fetchall()
            rx_dict['items'] = [dict(it) for it in items]
            history.append(rx_dict)

        patient_dict = dict(matched)
        if not patient_dict.get('patient_id'):
            patient_dict['patient_id'] = generate_patient_id(patient_id)

        return jsonify({
            'found': True,
            'patient': patient_dict,
            'history': history,
            'recurring_conditions': list(diagnoses_set)
        })

    # Return partial suggestions if not exact match
    like = f'%{q}%'
    suggestions = db.execute("""
        SELECT p.id, p.patient_id, p.name, p.phone, p.age, p.gender,
               COUNT(pr.id) as visit_count,
               MAX(pr.created_at) as last_visit,
               (SELECT diagnosis FROM prescriptions WHERE patient_id = p.id ORDER BY datetime(created_at) DESC, id DESC LIMIT 1) as latest_diagnosis
        FROM patients p
        LEFT JOIN prescriptions pr ON p.id = pr.patient_id
        WHERE p.name LIKE ? OR p.patient_id LIKE ? OR p.phone LIKE ?
        GROUP BY p.id
        ORDER BY p.updated_at DESC
        LIMIT 6
    """, (like, like, like)).fetchall()

    return jsonify({
        'found': False,
        'patient': None,
        'history': [],
        'suggestions': [dict(s) for s in suggestions]
    })

# ── Consultation & Prescription Sheet Management API ─────────────────────────

@app.route('/api/prescriptions/save', methods=['POST'])
def api_save_prescription():
    """
    Creates a new prescription/consultation record or updates the active in-progress consultation.
    - NEVER overwrites previous visits!
    - Every new consultation for a patient gets a separate visit_number and separate timestamp.
    - Accurately links medications to this consultation.
    - Updates patient profile with current allergies, medical history, and contact info.
    """
    data = request.get_json(silent=True) or {}
    patient_name = data.get('patient_name', '').strip()
    if not patient_name:
        return jsonify({'success': False, 'error': 'Patient Name is required.'}), 400

    items = data.get('items', [])
    if not items or len(items) == 0:
        return jsonify({'success': False, 'error': 'Please prescribe at least one medication.'}), 400

    phone = data.get('patient_phone', '').strip()
    age = data.get('patient_age', '').strip()
    gender = data.get('patient_gender', '').strip()
    address = data.get('patient_address', '').strip()
    allergies = data.get('allergies', '').strip()
    medical_history = data.get('medical_history', '').strip()

    complaints = data.get('complaints', '').strip()
    examination = data.get('examination', '').strip()
    diagnosis = data.get('diagnosis', '').strip()
    treatment_plan = data.get('treatment_plan', '').strip()
    follow_up = data.get('follow_up', '').strip()
    doctor_notes = data.get('doctor_notes', '').strip()

    patient_id = data.get('patient_id')
    prescription_id = data.get('prescription_id')
    is_new_visit = data.get('is_new_visit', False)

    db = get_db()
    norm_phone = clean_phone(phone)
    norm_name = clean_name(patient_name)

    # ── Step 1: Find or Register Patient Profile (Never Duplicate Patient) ────
    matched_patient = None

    if patient_id:
        matched_patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()

    if not matched_patient and norm_phone and len(norm_phone) >= 7:
        all_patients = db.execute("SELECT * FROM patients WHERE phone != ''").fetchall()
        for p in all_patients:
            if clean_phone(p['phone']) == norm_phone:
                matched_patient = p
                break

    if not matched_patient and norm_name:
        all_patients = db.execute("SELECT * FROM patients").fetchall()
        for p in all_patients:
            if clean_name(p['name']) == norm_name:
                matched_patient = p
                break

    if matched_patient:
        patient_id = matched_patient['id']
        db.execute("""
            UPDATE patients 
            SET name = ?,
                phone = CASE WHEN ? != '' THEN ? ELSE phone END,
                age = CASE WHEN ? != '' THEN ? ELSE age END,
                gender = CASE WHEN ? != '' THEN ? ELSE gender END,
                address = CASE WHEN ? != '' THEN ? ELSE address END,
                allergies = CASE WHEN ? != '' THEN ? ELSE allergies END,
                medical_history = CASE WHEN ? != '' THEN ? ELSE medical_history END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (patient_name, phone, phone, age, age, gender, gender, address, address,
              allergies, allergies, medical_history, medical_history, patient_id))
    else:
        cur = db.execute("""
            INSERT INTO patients (name, phone, age, gender, address, allergies, medical_history, updated_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (patient_name, phone, age, gender, address, allergies, medical_history))
        patient_id = cur.lastrowid
        db.execute("UPDATE patients SET patient_id = ? WHERE id = ?", (generate_patient_id(patient_id), patient_id))

    # ── Step 2: Save Consultation Record (Never Overwrite Previous Visits) ───
    existing_rx = None

    # If explicitly updating an already-saved consultation on the current desk sheet
    if prescription_id and not is_new_visit:
        existing_rx = db.execute(
            "SELECT id, visit_number FROM prescriptions WHERE id = ? AND patient_id = ?",
            (prescription_id, patient_id)
        ).fetchone()

    if existing_rx:
        # In-place update of current consultation (e.g. user clicked Save then Save & Print)
        rx_id = existing_rx['id']
        visit_number = existing_rx['visit_number'] or 1
        db.execute("""
            UPDATE prescriptions 
            SET patient_name = ?, patient_phone = ?, patient_age = ?, patient_gender = ?,
                complaints = ?, examination = ?, diagnosis = ?, treatment_plan = ?,
                follow_up = ?, doctor_notes = ?
            WHERE id = ?
        """, (patient_name, phone, age, gender, complaints, examination, diagnosis,
              treatment_plan, follow_up, doctor_notes, rx_id))
        # Clear items to re-insert cleanly
        db.execute("DELETE FROM prescription_items WHERE prescription_id = ?", (rx_id,))
        is_updated = True
    else:
        # NEW CONSULTATION: Calculate next sequential visit number for this patient
        prior_visits_count = db.execute(
            "SELECT COUNT(*) FROM prescriptions WHERE patient_id = ?",
            (patient_id,)
        ).fetchone()[0]
        visit_number = prior_visits_count + 1

        cur = db.execute("""
            INSERT INTO prescriptions 
            (patient_id, patient_name, patient_phone, patient_age, patient_gender, visit_number,
             complaints, examination, diagnosis, treatment_plan, follow_up, doctor_notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (patient_id, patient_name, phone, age, gender, visit_number,
              complaints, examination, diagnosis, treatment_plan, follow_up, doctor_notes))
        rx_id = cur.lastrowid
        is_updated = False

    # ── Step 3: Insert Prescribed Medication Items ────────────────────────────
    seen_keys = set()
    for it in items:
        med_name = (it.get('name') or it.get('medicine_name') or '').strip()
        dosage = it.get('dosage', '').strip()
        if not med_name:
            continue
        key = (med_name.lower(), dosage.lower())
        if key in seen_keys:
            continue
        seen_keys.add(key)

        urdu_text = (it.get('urdu') or it.get('urdu_instructions') or it.get('instructions') or '').strip()

        db.execute("""
            INSERT INTO prescription_items 
            (prescription_id, medicine_name, dosage, frequency, duration, urdu_instructions)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            rx_id,
            med_name,
            dosage,
            it.get('frequency', '').strip(),
            it.get('duration', '').strip(),
            urdu_text
        ))

    db.commit()

    patient_row = db.execute("SELECT patient_id FROM patients WHERE id = ?", (patient_id,)).fetchone()
    patient_code = patient_row['patient_id'] if patient_row else generate_patient_id(patient_id)

    return jsonify({
        'success': True,
        'prescription_id': rx_id,
        'patient_id': patient_id,
        'patient_code': patient_code,
        'visit_number': visit_number,
        'is_update': is_updated,
        'message': f'Consultation #{visit_number} saved for {patient_name}!'
    })

@app.route('/api/prescriptions/<int:rx_id>')
def api_get_prescription(rx_id):
    """Retrieve a single prescription sheet with all consultation fields and medications."""
    db = get_db()
    rx = db.execute("SELECT * FROM prescriptions WHERE id = ?", (rx_id,)).fetchone()
    if not rx:
        return jsonify({'error': 'Prescription not found'}), 404

    items = db.execute("SELECT * FROM prescription_items WHERE prescription_id = ? ORDER BY id ASC", (rx_id,)).fetchall()
    patient = db.execute("SELECT * FROM patients WHERE id = ?", (rx['patient_id'],)).fetchone() if rx['patient_id'] else None

    res = dict(rx)
    res['items'] = [dict(it) for it in items]
    res['patient_code'] = patient['patient_id'] if patient and patient['patient_id'] else (generate_patient_id(rx['patient_id']) if rx['patient_id'] else '—')
    res['patient_allergies'] = patient['allergies'] if patient else ''
    res['patient_medical_history'] = patient['medical_history'] if patient else ''

    return jsonify(res)

@app.route('/api/prescriptions/<int:rx_id>', methods=['DELETE'])
def api_delete_prescription(rx_id):
    """Delete a specific consultation/prescription record."""
    db = get_db()
    rx = db.execute("SELECT patient_name, visit_number FROM prescriptions WHERE id = ?", (rx_id,)).fetchone()
    if rx:
        db.execute("DELETE FROM prescriptions WHERE id = ?", (rx_id,))
        db.commit()
        return jsonify({'success': True, 'message': f'Consultation visit deleted.'})
    return jsonify({'success': False, 'error': 'Record not found'}), 404

@app.route('/api/records')
def api_records():
    """Retrieve master prescription log for quick search and historical auditing."""
    db = get_db()
    q = request.args.get('q', '').strip()
    sql = """
        SELECT pr.id, pr.patient_id, pr.patient_name, pr.patient_phone, pr.patient_age,
               pr.patient_gender, pr.visit_number, pr.complaints, pr.examination,
               pr.diagnosis, pr.treatment_plan, pr.follow_up, pr.doctor_notes, pr.created_at,
               p.patient_id as patient_code, p.allergies,
               COUNT(pi.id) as item_count,
               GROUP_CONCAT(pi.medicine_name, ', ') as medicines_preview
        FROM prescriptions pr
        LEFT JOIN patients p ON pr.patient_id = p.id
        LEFT JOIN prescription_items pi ON pr.id = pi.prescription_id
    """
    params = []
    if q:
        like = f"%{q}%"
        sql += " WHERE (pr.patient_name LIKE ? OR pr.patient_phone LIKE ? OR pr.diagnosis LIKE ? OR p.patient_id LIKE ?)"
        params.extend([like, like, like, like])

    sql += " GROUP BY pr.id ORDER BY datetime(pr.created_at) DESC, pr.id DESC LIMIT 80"
    rows = db.execute(sql, params).fetchall()
    return jsonify([dict(r) for r in rows])

# ── Helper Functions ─────────────────────────────────────────────────────────

def _extract_med_form():
    return {
        'name':              request.form.get('name', '').strip(),
        'category':          request.form.get('category', '').strip(),
        'default_dosage':    request.form.get('default_dosage', '').strip(),
        'default_frequency': request.form.get('default_frequency', '').strip(),
        'default_duration':  request.form.get('default_duration', '').strip(),
        'urdu_instructions': request.form.get('urdu_instructions', '').strip(),
        'notes':             request.form.get('notes', '').strip(),
    }

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5050, debug=True)
