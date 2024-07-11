from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.json
        phone_number = data.get('phone_number')
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400

        url = "https://web.udhaar.pk/udhaar/dukaan/create/sendotp/"
        headers = {
            "Host": "web.udhaar.pk",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://web.udhaar.pk",
            "Referer": "https://web.udhaar.pk/SignUp",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Content-Type": "application/json; charset=UTF-8"
        }

        payload = {
            "phone_number": phone_number,
            "referer": None,
            "version": "multi-business"
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 429:
            return jsonify({"error": "Rate limit exceeded, please try again later"}), 429
        if response.ok:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
