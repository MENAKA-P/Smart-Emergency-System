import sqlite3
import os


DATABASE = "database/hospital.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    os.makedirs("database", exist_ok=True)

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# CREATE DATABASE
# =========================================================

def create_database():

    db = get_db()

    cursor = db.cursor()


    # =====================================================
    # PATIENTS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            age INTEGER,

            gender TEXT,

            phone TEXT,

            email TEXT UNIQUE,

            password TEXT,

            blood_group TEXT,

            address TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # =====================================================
    # EMERGENCY CASES
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergency_cases (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id INTEGER,

            symptoms TEXT,

            department TEXT,

            procedure TEXT,

            emergency_level TEXT,

            priority_score INTEGER,

            bp TEXT,

            heart_rate INTEGER,

            oxygen INTEGER,

            consciousness TEXT,

            status TEXT DEFAULT 'Waiting',

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(patient_id)
                REFERENCES patients(id)
        )
    """)


    # =====================================================
    # DOCTORS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            department TEXT NOT NULL,

            doctor_type TEXT NOT NULL,

            phone TEXT,

            availability TEXT DEFAULT 'Available',

            emergency_duty INTEGER DEFAULT 1
        )
    """)


    # =====================================================
    # RECEPTIONISTS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receptionists (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            phone TEXT,

            availability TEXT DEFAULT 'Available'
        )
    """)


    # =====================================================
    # HOSPITALS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            hospital_name TEXT NOT NULL,

            phone TEXT NOT NULL,

            address TEXT,

            distance REAL,

            latitude REAL,

            longitude REAL,

            emergency_available INTEGER DEFAULT 1
        )
    """)


    # =====================================================
    # HOSPITAL DOCTORS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospital_doctors (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            hospital_id INTEGER,

            doctor_name TEXT,

            department TEXT,

            doctor_type TEXT,

            phone TEXT,

            availability TEXT DEFAULT 'Available',

            FOREIGN KEY(hospital_id)
                REFERENCES hospitals(id)
        )
    """)


    # =====================================================
    # APPOINTMENTS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id INTEGER NOT NULL,

            doctor_id INTEGER NOT NULL,

            appointment_date TEXT NOT NULL,

            appointment_time TEXT NOT NULL,

            reason TEXT,

            status TEXT DEFAULT 'Pending',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(patient_id)
                REFERENCES patients(id),

            FOREIGN KEY(doctor_id)
                REFERENCES doctors(id)
        )
    """)


    # =====================================================
    # ADMIN
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE,

            password TEXT
        )
    """)


    # =====================================================
    # DEFAULT ADMIN
    # =====================================================

    cursor.execute("""
        INSERT OR IGNORE INTO admins
        (
            username,
            password
        )

        VALUES (?, ?)
    """, (
        "admin",
        "admin123"
    ))


    # =====================================================
    # DEFAULT DOCTORS
    # =====================================================

    doctor_count = cursor.execute(
        "SELECT COUNT(*) FROM doctors"
    ).fetchone()[0]


    if doctor_count == 0:

        doctors = [

            (
                "Dr. Priya Sharma",
                "Cardiology",
                "Specialist",
                "9876543210",
                "Available",
                1
            ),

            (
                "Dr. Arun Kumar",
                "Neurology",
                "Specialist",
                "9876543211",
                "Unavailable",
                1
            ),

            (
                "Dr. Meena",
                "Orthopedics",
                "Specialist",
                "9876543212",
                "Available",
                1
            ),

            (
                "Dr. Rahul",
                "General Medicine",
                "Specialist",
                "9876543213",
                "Available",
                1
            ),

            (
                "Dr. Karthik",
                "Neurology",
                "Intern",
                "9876543214",
                "Available",
                1
            ),

            (
                "Dr. Divya",
                "Cardiology",
                "Intern",
                "9876543215",
                "Available",
                1
            ),

            (
                "Dr. Naveen",
                "Orthopedics",
                "Intern",
                "9876543216",
                "Busy",
                1
            )
        ]


        cursor.executemany("""
            INSERT INTO doctors
            (
                name,
                department,
                doctor_type,
                phone,
                availability,
                emergency_duty
            )

            VALUES (?, ?, ?, ?, ?, ?)
        """, doctors)


    # =====================================================
    # RECEPTIONISTS
    # =====================================================

    receptionist_count = cursor.execute(
        "SELECT COUNT(*) FROM receptionists"
    ).fetchone()[0]


    if receptionist_count == 0:

        receptionists = [

            (
                "Anitha",
                "9876500011",
                "Available"
            ),

            (
                "Kavya",
                "9876500012",
                "Available"
            ),

            (
                "Priya",
                "9876500013",
                "Busy"
            )
        ]


        cursor.executemany("""
            INSERT INTO receptionists
            (
                name,
                phone,
                availability
            )

            VALUES (?, ?, ?)
        """, receptionists)


    # =====================================================
    # SAMPLE NEARBY HOSPITALS
    # =====================================================

    hospital_count = cursor.execute(
        "SELECT COUNT(*) FROM hospitals"
    ).fetchone()[0]


    if hospital_count == 0:

        hospitals = [

            (
                "City Care Multispeciality Hospital",
                "9877000011",
                "Main Road",
                1.8,
                11.0168,
                76.9558,
                1
            ),

            (
                "Sri Health Emergency Hospital",
                "9877000022",
                "Hospital Road",
                3.2,
                11.0210,
                76.9600,
                1
            ),

            (
                "LifeLine Medical Centre",
                "9877000033",
                "Central Avenue",
                4.7,
                11.0280,
                76.9700,
                1
            )
        ]


        cursor.executemany("""
            INSERT INTO hospitals
            (
                hospital_name,
                phone,
                address,
                distance,
                latitude,
                longitude,
                emergency_available
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, hospitals)


    # =====================================================
    # SAMPLE HOSPITAL INTERNS
    # =====================================================

    hospital_doctor_count = cursor.execute(
        "SELECT COUNT(*) FROM hospital_doctors"
    ).fetchone()[0]


    if hospital_doctor_count == 0:

        hospital_doctors = [

            (
                1,
                "Dr. Vishal",
                "Neurology",
                "Intern",
                "9000000011",
                "Available"
            ),

            (
                1,
                "Dr. Sneha",
                "Cardiology",
                "Intern",
                "9000000012",
                "Available"
            ),

            (
                2,
                "Dr. Ajay",
                "Neurology",
                "Intern",
                "9000000021",
                "Available"
            ),

            (
                2,
                "Dr. Priyanka",
                "Orthopedics",
                "Intern",
                "9000000022",
                "Busy"
            ),

            (
                3,
                "Dr. Santhosh",
                "Neurology",
                "Intern",
                "9000000031",
                "Available"
            )
        ]


        cursor.executemany("""
            INSERT INTO hospital_doctors
            (
                hospital_id,
                doctor_name,
                department,
                doctor_type,
                phone,
                availability
            )

            VALUES (?, ?, ?, ?, ?, ?)
        """, hospital_doctors)


    # =====================================================
    # SAVE DATABASE
    # =====================================================

    db.commit()

    db.close()


# =========================================================
# RUN DATABASE
# =========================================================

if __name__ == "__main__":

    create_database()

    print("Database created successfully.")