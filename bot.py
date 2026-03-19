from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
import os

flask_app = Flask(__name__)
CORS(flask_app, origins="*")

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

@flask_app.route('/send-checkin-email', methods=['POST'])
def send_email():
    try:
        data = request.json
        if data.get("secret") != WEBHOOK_SECRET:
            return jsonify({"error": "no"}), 403

        email_dest = data.get("email_dest", "")

        msg = MIMEText("Test - Check-in completato!\n\nSe ricevi questa email, l'invio Gmail funziona. Il PDF arriverà nella versione finale.")
        msg["From"] = EMAIL_SENDER
        msg["To"] = email_dest
        msg["Subject"] = "Test Self Check-in Amour Içi"

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, email_dest, msg.as_string())

        print("✅ EMAIL TEST INVIATA CON SUCCESSO!")
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Errore:", e)
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)