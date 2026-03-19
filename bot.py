from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

flask_app = Flask(__name__)
CORS(flask_app, origins="*")   # ← Questo risolve il blocco

# ================== VARIABILI SICURE ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# ================== PDF ==================
PDF_FILES = {
    "Deluxe Apartment": "studio_deluxe.pdf",
    "Studio Apartment": "studio_deluxe.pdf",
}

@flask_app.route('/')
def home():
    return "✅ Bot AmourIci ONLINE e pronto!"

@flask_app.route('/send-checkin-email', methods=['POST'])
def send_email():
    try:
        data = request.json
        if data.get("secret") != WEBHOOK_SECRET:
            return jsonify({"error": "no"}), 403

        appartamento = data.get("appartamento", "")
        email_dest = data.get("email_dest", "")

        pdf_filename = PDF_FILES.get(appartamento)
        if not pdf_filename:
            return jsonify({"error": "PDF non trovato"}), 404

        html = f"""
        <html><body style="font-family:Arial;background:#f4f4f4;padding:20px;">
        <div style="max-width:600px;margin:auto;background:white;border-radius:12px;">
            <div style="background:#000;color:white;padding:25px;text-align:center;">
                <h1>AMOUR IÇI</h1>
            </div>
            <div style="padding:30px;">
                <h2>Ciao 👋</h2>
                <p>Check-in completato!</p>
                <p><strong>Appartamento:</strong> {appartamento}</p>
                <p><strong>Data:</strong> {data.get('data', '')}</p>
                <h3>📎 PDF istruzioni in allegato</h3>
            </div>
        </div>
        </body></html>
        """

        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_SENDER
        msg["To"] = email_dest
        msg["Subject"] = f"Self Check-in - {appartamento} - Amour Içi"

        msg.attach(MIMEText(html, "html"))

        with open(pdf_filename, "rb") as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
            pdf_attachment.add_header("Content-Disposition", "attachment", filename=pdf_filename)
            msg.attach(pdf_attachment)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, email_dest, msg.as_string())

        print(f"✅ Email + PDF inviati a {email_dest}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Errore:", e)
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)