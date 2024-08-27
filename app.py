from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import asyncio
import aiohttp
import logging

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

async def send_request(session, url, method="POST", headers=None, json=None, data=None):
    try:
        async with session.request(method, url, headers=headers, json=json, data=data) as response:
            status_code = response.status
            text = await response.text()
            logger.info(f"Request to {url} completed with status {status_code}")
            return {"url": url, "status_code": status_code, "response": text}
    except Exception as e:
        logger.error(f"Request to {url} failed: {str(e)}")
        return {"url": url, "error": str(e)}

async def send_all_requests(phone_number):
    async with aiohttp.ClientSession() as session:
        tasks = []

        # First API request
        url1 = "https://web.udhaar.pk/udhaar/dukaan/create/sendotp/"
        headers1 = {
            "Host": "web.udhaar.pk",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json; charset=UTF-8"
        }
        payload1 = {
            "phone_number": phone_number,
            "referer": None,
            "version": "multi-business"
        }
        tasks.append(send_request(session, url1, headers=headers1, json=payload1))

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
        tasks.append(send_request(session, url2, method="GET", json=params2))

        # Third API request
        if phone_number.startswith('0'):
            phone_number = '92' + phone_number[1:]
        
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
        tasks.append(send_request(session, url3, headers=headers3, data=data1))

        # Fourth API request
        url4 = "https://portallapp.com/api/v1/auth/generate-otp"
        payload4 = {
            "mobile_no": phone_number[-10:]  # Extract the last 10 digits for mobile_no
        }
        tasks.append(send_request(session, url4, json=payload4))

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
        tasks.append(send_request(session, url5, headers=headers5, data=data5))

        # Gather results from all requests
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

@app.route('/send-otp', methods=['POST'])
async def send_otp():
    try:
        data = request.json
        phone_number = data.get('phone_number')
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400

        logger.info(f"Received request to send OTP to {phone_number}")

        # Send all requests concurrently
        results = await send_all_requests(phone_number)

        return jsonify({"success": True, "message": "OTP requests sent", "results": results}), 200
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
