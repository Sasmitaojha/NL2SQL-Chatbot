import sqlite3
import random
from datetime import datetime, timedelta

def create_database():
    conn = sqlite3.connect('clinic.db')
    cursor = conn.cursor()

    # Table 1: patients
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        date_of_birth DATE,
        gender TEXT,
        city TEXT,
        registered_date DATE
    )
    ''')

    # Table 2: doctors
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT,
        department TEXT,
        phone TEXT
    )
    ''')

    # Table 3: appointments
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        appointment_date DATETIME,
        status TEXT,
        notes TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    )
    ''')

    # Table 4: treatments
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS treatments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER,
        treatment_name TEXT,
        cost REAL,
        duration_minutes INTEGER,
        FOREIGN KEY (appointment_id) REFERENCES appointments(id)
    )
    ''')

    # Table 5: invoices
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        invoice_date DATE,
        total_amount REAL,
        paid_amount REAL,
        status TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    )
    ''')

    conn.commit()
    return conn

def insert_dummy_data(conn):
    cursor = conn.cursor()
    random.seed(42) # For reproducibility

    # -- DOCTORS --
    specializations = ['Dermatology', 'Cardiology', 'Orthopedics', 'General', 'Pediatrics']
    doctors = []
    for i in range(15):
        spec = random.choice(specializations)
        name = f"Dr. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'])} {random.choice(['A.', 'B.', 'C.', 'D.', 'E.'])}"
        doctors.append((name, spec, spec + ' Dept', f'555-01{i:02d}'))
    
    cursor.executemany("INSERT INTO doctors (name, specialization, department, phone) VALUES (?, ?, ?, ?)", doctors)
    
    # -- PATIENTS --
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
    first_names = ['James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer', 'Michael', 'Linda', 'David', 'Elizabeth', 'William', 'Barbara', 'Richard', 'Susan', 'Joseph']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson']
    
    patients = []
    for i in range(200):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        email = f"{fname.lower()}.{lname.lower()}{i}@example.com" if random.random() > 0.2 else None
        phone = f"555-02{i%100:02d}" if random.random() > 0.1 else None
        
        dob_year = random.randint(1950, 2018)
        dob = f"{dob_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        
        gender = random.choice(['M', 'F'])
        city = random.choice(cities)
        
        reg_date = datetime.now() - timedelta(days=random.randint(0, 365))
        reg_date_str = reg_date.strftime('%Y-%m-%d')
        
        patients.append((fname, lname, email, phone, dob, gender, city, reg_date_str))
        
    cursor.executemany("INSERT INTO patients (first_name, last_name, email, phone, date_of_birth, gender, city, registered_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", patients)
    
    # -- APPOINTMENTS --
    statuses = ['Scheduled', 'Completed', 'Cancelled', 'No-Show']
    # Add weights to statuses: 70% completed, 10% scheduled, 10% cancelled, 10% no-show
    status_weights = [0.1, 0.7, 0.1, 0.1]
    
    completed_appointments = [] # save for treatments
    appointments = []
    for i in range(500):
        patient_id = random.randint(1, 200)
        doctor_id = random.randint(1, 15)
        
        # Last 12 months spread
        app_date = datetime.now() - timedelta(days=random.randint(0, 365))
        app_date = app_date.replace(hour=random.randint(8, 17), minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0)
        app_date_str = app_date.strftime('%Y-%m-%d %H:%M:%S')
        
        status = random.choices(statuses, weights=status_weights)[0]
        
        notes = "Patient reported mild symptoms" if random.random() > 0.5 else None
        
        appointments.append((patient_id, doctor_id, app_date_str, status, notes))
        
    cursor.executemany("INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, notes) VALUES (?, ?, ?, ?, ?)", appointments)
    
    # fetch appointments to get IDs for completed ones
    cursor.execute("SELECT id, status FROM appointments")
    all_apps = cursor.fetchall()
    completed_app_ids = [app[0] for app in all_apps if app[1] == 'Completed']
    
    # -- TREATMENTS --
    treatment_names = ['Consultation', 'Blood Test', 'X-Ray', 'MRI', 'Physical Therapy', 'Surgery', 'Vaccination', 'Checkup']
    treatments = []
    
    # We need 350 treatments linked to completed appointments
    selected_app_ids = random.choices(completed_app_ids, k=350)
    for app_id in selected_app_ids:
        t_name = random.choice(treatment_names)
        cost = round(random.uniform(50, 5000), 2)
        duration = random.choice([15, 30, 45, 60, 120])
        treatments.append((app_id, t_name, cost, duration))
        
    cursor.executemany("INSERT INTO treatments (appointment_id, treatment_name, cost, duration_minutes) VALUES (?, ?, ?, ?)", treatments)
    
    # -- INVOICES --
    # 300 invoices with Paid, Pending, Overdue
    invoices = []
    inv_statuses = ['Paid', 'Pending', 'Overdue']
    for i in range(300):
        patient_id = random.randint(1, 200)
        inv_date = datetime.now() - timedelta(days=random.randint(0, 365))
        inv_date_str = inv_date.strftime('%Y-%m-%d')
        
        total_amt = round(random.uniform(50, 5000), 2)
        status = random.choice(inv_statuses)
        
        if status == 'Paid':
            paid_amt = total_amt
        elif status == 'Pending':
            paid_amt = round(total_amt * random.uniform(0, 0.5), 2)
        else: # Overdue
            paid_amt = 0.0
            
        invoices.append((patient_id, inv_date_str, total_amt, paid_amt, status))
        
    cursor.executemany("INSERT INTO invoices (patient_id, invoice_date, total_amount, paid_amount, status) VALUES (?, ?, ?, ?, ?)", invoices)
    
    conn.commit()
    
    # Summary
    cursor.execute("SELECT count(*) FROM patients")
    p_count = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM doctors")
    d_count = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM appointments")
    a_count = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM treatments")
    t_count = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM invoices")
    i_count = cursor.fetchone()[0]
    
    print(f"Created {p_count} patients, {d_count} doctors, {a_count} appointments, {t_count} treatments, {i_count} invoices.")
    
if __name__ == "__main__":
    import os
    if os.path.exists('clinic.db'):
        os.remove('clinic.db')
        print("Removed old database clinic.db")
    conn = create_database()
    insert_dummy_data(conn)
    conn.close()
    print("Database creation and seeding complete.")
