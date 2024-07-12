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

        # First API request
        url1 = "https://web.udhaar.pk/udhaar/dukaan/create/sendotp/"
        headers1 = {
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
        payload1 = {
            "phone_number": phone_number,
            "referer": None,
            "version": "multi-business"
        }
        response1 = requests.post(url1, headers=headers1, json=payload1)
        if response1.status_code == 429:
            return jsonify({"error": "Rate limit exceeded, please try again later"}), 429
        if not response1.ok:
            return jsonify({"error": response1.text}), response1.status_code

        # Second API request
        url2 = "https://staging.cricwick.net:13002/api/send_pin"
        params2 = {
            "telco": "easypaisa",
            "phone": phone_number,
            "sub_type": "",
            "source": 2,
            "sub_source": "CricwickWeb",
            "is_bundle": 1,
            "bundle_id": 13
        }
        response2 = requests.get(url2, params=params2)
        if response2.status_code != 200:
            return jsonify({"error": f"Failed to send OTP to Cricwick. Status code: {response2.status_code}"}), response2.status_code

        return jsonify({"success": True, "message": "OTP requests sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
