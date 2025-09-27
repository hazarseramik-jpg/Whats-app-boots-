# app.py
import os
from flask import Flask, request, Response
import requests
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

# Ortam değişkenleri
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")  # örn: "whatsapp:+14155238886"

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
app = Flask(__name__)

def ask_openai(prompt: str) -> str:
    url = "https://api.openai.com/v1/responses"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",  # modeli buradan değiştirebilirsin
        "input": prompt
    }
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    resp.raise_for_status()
    out = resp.json()
    try:
        return out["output"][0]["content"][0]["text"]
    except Exception:
        return str(out)

@app.route("/webhook", methods=["POST"])
def webhook():
    from_number = request.form.get("From")
    body = request.form.get("Body", "").strip()

    if body.startswith("/"):
        reply = f"Komut algılandı: {body}\n(Not: Komutlar için henüz eğitim aşamasındayız.)"
    else:
        prompt = f"Kullanıcı mesajı: {body}\nKısa ve nazik bir yanıt ver."
        try:
            reply = ask_openai(prompt)
        except Exception:
            reply = "Üzgünüm, yanıt oluşturulamadı. Lütfen sonra tekrar dene."

    resp = MessagingResponse()
    resp.message(reply)
    return Response(str(resp), mimetype="application/xml")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
