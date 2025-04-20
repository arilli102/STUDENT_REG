# app.py
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import smtplib
import random
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = 'your_flask_secret_key'

# ---------- MySQL Configuration ----------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2002",
    database="student_db"
)
cursor = db.cursor()

# ---------- OTP Email Sender ----------
def send_otp_email(receiver_email, otp):
    msg = EmailMessage()
    msg['Subject'] = 'Your OTP Verification Code'
    msg['From'] = 'jdeesh151@gmail.com'
    msg['To'] = receiver_email
    msg.set_content(f'Hello!\n\nYour OTP code is: {otp}\n\nUse this to verify your registration.')

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login('jdeesh151@gmail.com', 'vignrunbhcczuefm')
            smtp.send_message(msg)
            return True
    except Exception as e:
        print("\u274c Failed to send OTP:", e)
        return False

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/submit', methods=['POST'])
def submit():
    student_data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'dob': request.form['dob'],
        'gender': request.form['gender'],
        'nationality': request.form['nationality'],
        'email': request.form['email'],
        'phone': request.form['phone'],
        'address': request.form['address'],
        'emergency_contact': request.form['emergency_contact'],
        'education_level': request.form['education_level'],
        'previous_school': request.form['previous_school']
    }
    session['student_data'] = student_data

    otp = str(random.randint(100000, 999999))
    session['otp'] = otp

    if send_otp_email(student_data['email'], otp):
        return render_template('verify_otp.html', email=student_data['email'])
    else:
        return "\u274c Failed to send OTP. Try again later."

@app.route('/verify', methods=['POST'])
def verify():
    entered_otp = request.form['otp']

    if entered_otp == session.get('otp'):
        data = session['student_data']

        insert_sql = """
            INSERT INTO students (
                first_name, last_name, dob, gender, nationality,
                email, phone, address, emergency_contact,
                education_level, previous_school, is_verified
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        """
        values = (
            data['first_name'], data['last_name'], data['dob'], data['gender'], data['nationality'],
            data['email'], data['phone'], data['address'], data['emergency_contact'],
            data['education_level'], data['previous_school']
        )
        cursor.execute(insert_sql, values)
        db.commit()

        student_id = cursor.lastrowid
        student_uid = f"STU{student_id:04d}"
        cursor.execute("UPDATE students SET student_uid = %s WHERE id = %s", (student_uid, student_id))
        db.commit()

        # ✅ Send confirmation email here
        send_confirmation_email(data['email'], student_uid)

        return render_template('success.html', student_id=student_uid, email=data['email'])
    else:
        return "❌ Invalid OTP. Please try again."


def send_confirmation_email(receiver_email, student_uid):
    student = session['student_data']  # you can also pass this directly if you prefer

    msg = EmailMessage()
    msg['Subject'] = '🎓 Registration Successful - Your Student ID'
    msg['From'] = 'jdeesh151@gmail.com'
    msg['To'] = receiver_email

    msg.set_content(f"""
Hello {student['first_name']} {student['last_name']},

🎉 Congratulations! Your registration is successful.

Here are your registration details:

📧 Email: {receiver_email}
🎂 Date of Birth: {student['dob']}
🆔 Student ID: {student_uid}

Thank you for registering with us!

Best regards,  
Student Affairs Team
    """)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login('jdeesh151@gmail.com', 'vignrunbhcczuefm')
            smtp.send_message(msg)
            print("✅ Confirmation email sent.")
    except Exception as e:
        print("❌ Failed to send confirmation email:", e)



if __name__ == '__main__':
    app.run(debug=True)
