import smtplib
import random
from email.message import EmailMessage

def send_otp_via_smtp(receiver_email):
    otp = str(random.randint(100000, 999999))

    msg = EmailMessage()
    msg['Subject'] = 'Your OTP Code'
    msg['From'] = 'jdeesh151@gmail.com'
    msg['To'] = receiver_email
    msg.set_content(f'Your OTP is: {otp}')

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login('jdeesh151@gmail.com', 'vignrunbhcczuefm')  # use app password
            smtp.send_message(msg)
            print(f"✅ OTP sent to {receiver_email}: {otp}")
            return otp
    except Exception as e:
        print("❌ Failed to send OTP:", e)
        return None

# Example usage
send_otp_via_smtp('jd20041022@gmail.com')
