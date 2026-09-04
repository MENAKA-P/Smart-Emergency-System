from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db, create_database
from datetime import datetime, timedelta
import threading


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)
app.secret_key = "smart-hospital-secret-key"

# Create database
create_database()


# =========================================================
# WINDOWS EMERGENCY ALARM
# =========================================================

try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False


def emergency_alert():
    """
    Emergency alarm.
    Alarm duration = 10 seconds.
    """

    print("\n" + "=" * 60)
    print("🚨 EMERGENCY ALERT 🚨")
    print("Emergency patient arrived!")
    print("Administration has been notified.")
    print("🔊 Alarm started for 10 seconds")
    print("=" * 60)

    if not SOUND_AVAILABLE:
        print("Windows sound is not available.")
        return

    end_time = datetime.now() + timedelta(seconds=10)

    while datetime.now() < end_time:
        try:
            winsound.Beep(1200, 1000)
        except Exception as error:
            print("Alarm error:", error)
            break


def start_emergency_alarm():
    """
    Start alarm without stopping the Flask website.
    """

    thread = threading.Thread(
        target=emergency_alert,
        daemon=True
    )

    thread.start()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    db = get_db()

    try:

        doctor_count = db.execute(
            "SELECT COUNT(*) FROM doctors"
        ).fetchone()[0]

        available_doctors = db.execute(
            """
            SELECT COUNT(*)
            FROM doctors
            WHERE availability = 'Available'
            """
        ).fetchone()[0]

        emergency_count = db.execute(
            """
            SELECT COUNT(*)
            FROM emergency_cases
            WHERE status != 'Completed'
            """
        ).fetchone()[0]

        reception_available = db.execute(
            """
            SELECT COUNT(*)
            FROM receptionists
            WHERE availability = 'Available'
            """
        ).fetchone()[0]

    except Exception as error:

        print("Home page database error:", error)

        doctor_count = 0
        available_doctors = 0
        emergency_count = 0
        reception_available = 0

    finally:
        db.close()

    return render_template(
        "index.html",
        doctor_count=doctor_count,
        available_doctors=available_doctors,
        emergency_count=emergency_count,
        reception_available=reception_available
    )


# =========================================================
# PATIENT REGISTER
# =========================================================

@app.route("/patient/register", methods=["GET", "POST"])
def patient_register():

    if request.method == "POST":

        name = request.form.get("name", "")
        age = request.form.get("age", "")
        gender = request.form.get("gender", "")
        phone = request.form.get("phone", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        blood_group = request.form.get("blood_group", "")
        address = request.form.get("address", "")

        db = get_db()

        try:

            db.execute(
                """
                INSERT INTO patients
                (
                    name,
                    age,
                    gender,
                    phone,
                    email,
                    password,
                    blood_group,
                    address
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    age,
                    gender,
                    phone,
                    email,
                    password,
                    blood_group,
                    address
                )
            )

            db.commit()

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(
                url_for("patient_login")
            )

        except Exception as error:

            print("Patient registration error:", error)

            flash(
                "Registration failed. Email may already exist.",
                "danger"
            )

        finally:
            db.close()

    return render_template(
        "patient_register.html"
    )


# =========================================================
# PATIENT LOGIN
# =========================================================

@app.route("/patient/login", methods=["GET", "POST"])
def patient_login():

    if request.method == "POST":

        email = request.form.get("email", "")
        password = request.form.get("password", "")

        db = get_db()

        try:

            patient = db.execute(
                """
                SELECT *
                FROM patients
                WHERE email = ?
                AND password = ?
                """,
                (email, password)
            ).fetchone()

        except Exception as error:

            print("Patient login error:", error)
            patient = None

        db.close()

        if patient:

            session["patient_id"] = patient["id"]
            session["patient_name"] = patient["name"]

            return redirect(
                url_for("patient_dashboard")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "patient_login.html"
    )
# =========================================================
# BOOK APPOINTMENT
# =========================================================

@app.route("/appointment", methods=["GET", "POST"])
def appointment():

    if "patient_id" not in session:

        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for("patient_login")
        )

    db = get_db()

    if request.method == "POST":

        doctor_id = request.form.get("doctor_id")
        appointment_date = request.form.get("appointment_date")
        appointment_time = request.form.get("appointment_time")
        reason = request.form.get("reason", "")

        try:

            db.execute(
                """
                INSERT INTO appointments
                (
                    patient_id,
                    doctor_id,
                    appointment_date,
                    appointment_time,
                    reason
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session["patient_id"],
                    doctor_id,
                    appointment_date,
                    appointment_time,
                    reason
                )
            )

            db.commit()

            flash(
                "Appointment booked successfully!",
                "success"
            )

            return redirect(
                url_for("my_appointments")
            )

        except Exception as error:

            print("Appointment error:", error)

            flash(
                "Unable to book appointment.",
                "danger"
            )

    doctors = db.execute(
        """
        SELECT *
        FROM doctors
        WHERE availability = 'Available'
        ORDER BY department, name
        """
    ).fetchall()

    db.close()

    return render_template(
        "appointment.html",
        doctors=doctors
    )


# =========================================================
# MY APPOINTMENTS
# =========================================================

@app.route("/my-appointments")
def my_appointments():

    if "patient_id" not in session:

        return redirect(
            url_for("patient_login")
        )

    db = get_db()

    appointments = db.execute(
        """
        SELECT
            appointments.*,
            doctors.name AS doctor_name,
            doctors.department AS department,
            doctors.phone AS doctor_phone

        FROM appointments

        JOIN doctors
        ON appointments.doctor_id = doctors.id

        WHERE appointments.patient_id = ?

        ORDER BY
            appointment_date ASC,
            appointment_time ASC
        """,
        (session["patient_id"],)
    ).fetchall()

    db.close()

    return render_template(
        "my_appointments.html",
        appointments=appointments
    )

# =========================================================
# PATIENT DASHBOARD
# =========================================================

@app.route("/patient/dashboard")
def patient_dashboard():

    if "patient_id" not in session:

        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for("patient_login")
        )

    db = get_db()

    patient = db.execute(
        """
        SELECT *
        FROM patients
        WHERE id = ?
        """,
        (session["patient_id"],)
    ).fetchone()

    cases = db.execute(
        """
        SELECT *
        FROM emergency_cases
        WHERE patient_id = ?
        ORDER BY id DESC
        """,
        (session["patient_id"],)
    ).fetchall()

    db.close()

    return render_template(
        "patient_dashboard.html",
        patient=patient,
        cases=cases
    )


# =========================================================
# EMERGENCY REGISTRATION
# =========================================================

@app.route("/emergency", methods=["GET", "POST"])
def emergency():

    if "patient_id" not in session:

        flash(
            "Please login before submitting an emergency case.",
            "warning"
        )

        return redirect(
            url_for("patient_login")
        )

    if request.method == "POST":

        symptoms = request.form.get(
            "symptoms",
            ""
        )

        department = request.form.get(
            "department",
            ""
        )

        procedure = request.form.get(
            "procedure",
            ""
        )

        bp = request.form.get(
            "bp",
            ""
        )

        consciousness = request.form.get(
            "consciousness",
            ""
        )

        # -------------------------------------------------
        # HEART RATE
        # -------------------------------------------------

        try:

            heart_rate = int(
                request.form.get(
                    "heart_rate",
                    0
                )
            )

        except ValueError:

            heart_rate = 0


        # -------------------------------------------------
        # OXYGEN
        # -------------------------------------------------

        try:

            oxygen = int(
                request.form.get(
                    "oxygen",
                    0
                )
            )

        except ValueError:

            oxygen = 0


        # =================================================
        # PRIORITY SCORE
        # =================================================

        score = 0


        # Oxygen

        if oxygen > 0:

            if oxygen < 90:
                score += 40

            elif oxygen < 94:
                score += 25


        # Heart rate

        if heart_rate > 120:
            score += 20

        elif 0 < heart_rate < 50:
            score += 20


        # Consciousness

        if consciousness == "Unconscious":
            score += 40

        elif consciousness == "Confused":
            score += 25


        # Blood pressure

        if bp:

            try:

                systolic = int(
                    bp.split("/")[0]
                )

                if systolic < 90:
                    score += 30

                elif systolic > 180:
                    score += 25

            except ValueError:
                pass


        # =================================================
        # EMERGENCY LEVEL
        # =================================================

        if score >= 70:

            emergency_level = "Critical"

        elif score >= 40:

            emergency_level = "High"

        elif score >= 20:

            emergency_level = "Medium"

        else:

            emergency_level = "Low"


        # =================================================
        # SAVE EMERGENCY
        # =================================================

        db = get_db()

        try:

            db.execute(
                """
                INSERT INTO emergency_cases
                (
                    patient_id,
                    symptoms,
                    department,
                    procedure,
                    emergency_level,
                    priority_score,
                    bp,
                    heart_rate,
                    oxygen,
                    consciousness
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["patient_id"],
                    symptoms,
                    department,
                    procedure,
                    emergency_level,
                    score,
                    bp,
                    heart_rate,
                    oxygen,
                    consciousness
                )
            )

            db.commit()

        except Exception as error:

            print(
                "Emergency database error:",
                error
            )

            db.close()

            flash(
                "Unable to save emergency information.",
                "danger"
            )

            return redirect(
                url_for("patient_dashboard")
            )

        db.close()


        # =================================================
        # START ALARM
        # =================================================

        start_emergency_alarm()


        # =================================================
        # SHOW RESULT
        # =================================================

        return redirect(
            url_for(
                "emergency_result",
                department=department
            )
        )

    return render_template(
        "emergency.html"
    )


# =========================================================
# EMERGENCY RESULT
# =========================================================

@app.route("/emergency/result")
def emergency_result():

    if "patient_id" not in session:

        return redirect(
            url_for("patient_login")
        )

    department = request.args.get(
        "department",
        ""
    )

    db = get_db()


    # =====================================================
    # SPECIALIST
    # =====================================================

    doctor = db.execute(
        """
        SELECT *
        FROM doctors
        WHERE department = ?
        AND doctor_type = 'Specialist'
        AND availability = 'Available'
        LIMIT 1
        """,
        (department,)
    ).fetchone()


    # =====================================================
    # INTERN
    # =====================================================

    intern = db.execute(
        """
        SELECT *
        FROM doctors
        WHERE department = ?
        AND doctor_type = 'Intern'
        AND availability = 'Available'
        LIMIT 1
        """,
        (department,)
    ).fetchone()


    # =====================================================
    # RECEPTIONIST
    # =====================================================

    reception = db.execute(
        """
        SELECT *
        FROM receptionists
        WHERE availability = 'Available'
        LIMIT 1
        """
    ).fetchone()


    # =====================================================
    # NEARBY HOSPITALS
    # =====================================================

    hospitals = []


    if doctor is None:

        try:

            hospitals = db.execute(
                """
                SELECT
                    h.*,
                    hd.doctor_name,
                    hd.doctor_type,
                    hd.phone AS doctor_phone

                FROM hospitals h

                LEFT JOIN hospital_doctors hd

                ON h.id = hd.hospital_id

                AND hd.department = ?

                AND hd.availability = 'Available'

                WHERE h.emergency_available = 1

                ORDER BY h.distance ASC
                """,
                (department,)
            ).fetchall()

        except Exception as error:

            print(
                "Hospital referral error:",
                error
            )

            hospitals = []


    db.close()


    return render_template(
        "referral.html",
        department=department,
        doctor=doctor,
        intern=intern,
        reception=reception,
        hospitals=hospitals
    )


# =========================================================
# DOCTOR PAGE
# =========================================================

@app.route("/doctors")
def doctors():

    db = get_db()

    try:

        doctors = db.execute(
            """
            SELECT *
            FROM doctors
            ORDER BY department
            """
        ).fetchall()

    except Exception as error:

        print("Doctor page error:", error)
        doctors = []

    db.close()

    return render_template(
        "doctors.html",
        doctors=doctors
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        )

        password = request.form.get(
            "password",
            ""
        )

        db = get_db()

        try:

            admin = db.execute(
                """
                SELECT *
                FROM admins
                WHERE username = ?
                AND password = ?
                LIMIT 1
                """,
                (
                    username,
                    password
                )
            ).fetchone()

        except Exception as error:

            print(
                "Admin login error:",
                error
            )

            admin = None

        db.close()


        if admin:

            session["admin"] = admin["username"]

            return redirect(
                url_for("admin_dashboard")
            )

        flash(
            "Invalid administrator username or password.",
            "danger"
        )


    return render_template(
        "admin_login.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin" not in session:

        flash(
            "Please login as administrator.",
            "warning"
        )

        return redirect(
            url_for("admin_login")
        )

    db = get_db()


    # =====================================================
    # PATIENTS
    # =====================================================

    try:

        patients = db.execute(
            """
            SELECT *
            FROM patients
            ORDER BY id DESC
            """
        ).fetchall()

    except Exception:

        patients = []


    # =====================================================
    # EMERGENCY CASES
    # =====================================================

    try:

        emergencies = db.execute(
            """
            SELECT
                emergency_cases.*,
                patients.name AS patient_name,
                patients.phone AS patient_phone

            FROM emergency_cases

            JOIN patients

            ON emergency_cases.patient_id =
               patients.id

            ORDER BY
                priority_score DESC,
                emergency_cases.id DESC
            """
        ).fetchall()

    except Exception as error:

        print(
            "Emergency dashboard error:",
            error
        )

        emergencies = []


    # =====================================================
    # DOCTORS
    # =====================================================

    try:

        doctors = db.execute(
            """
            SELECT *
            FROM doctors
            ORDER BY department
            """
        ).fetchall()

    except Exception:

        doctors = []


    # =====================================================
    # RECEPTIONISTS
    # =====================================================

    try:

        receptionists = db.execute(
            """
            SELECT *
            FROM receptionists
            """
        ).fetchall()

    except Exception:

        receptionists = []


    # =====================================================
    # HOSPITALS
    # =====================================================

    try:

        hospitals = db.execute(
            """
            SELECT *
            FROM hospitals
            ORDER BY distance
            """
        ).fetchall()

    except Exception:

        hospitals = []


    db.close()


    # =====================================================
    # DASHBOARD COUNTS
    # =====================================================

    patient_count = len(patients)

    emergency_count = len(emergencies)

    doctor_count = len(doctors)

    receptionist_count = len(receptionists)

    hospital_count = len(hospitals)


    return render_template(
        "admin_dashboard.html",

        patients=patients,

        emergencies=emergencies,

        doctors=doctors,

        receptionists=receptionists,

        hospitals=hospitals,

        patient_count=patient_count,

        emergency_count=emergency_count,

        doctor_count=doctor_count,

        receptionist_count=receptionist_count,

        hospital_count=hospital_count
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect(
        url_for("index")
    )


# =========================================================
# GENERAL LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("index")
    )


# =========================================================
# 404 ERROR
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <h1>404 - Page Not Found</h1>
    <p>The requested page does not exist.</p>
    """, 404


# =========================================================
# 500 ERROR
# =========================================================

@app.errorhandler(500)
def server_error(error):

    return """
    <h1>500 - Server Error</h1>
    <p>Something went wrong on the server.</p>
    """, 500


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )

