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

# Function to send asynchronous POST requests
async def send_post_request(url, headers=None, data=None, json=None):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, data=data, json=json) as response:
                response_data = await response.json()
                logger.info(f"Request to {url} succeeded with status {response.status}")
                return {"status": response.status, "response": response_data}
        except Exception as e:
            logger.error(f"Request to {url} failed: {e}")
            return {"error": str(e)}

# Function to handle each API independently
async def handle_api_request(api_name, request_function, delay):
    await asyncio.sleep(delay)  # Delay to avoid hitting rate limits
    logger.info(f"Starting {api_name} after {delay} seconds delay")
    result = await request_function()
    if "error" in result:
        logger.error(f"{api_name} failed: {result['error']}")
    else:
        logger.info(f"{api_name} succeeded: {result['response']}")
    return {api_name: result}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-otp', methods=['POST'])
async def send_otp():
    data = request.json
    phone_number = data.get('phone_number')
    if not phone_number:
        return jsonify({"error": "Phone number is required"}), 400

    logger.info(f"Received request to send OTP to {phone_number}")

    tasks = []

    # Define the request functions for each API
    tasks.append(handle_api_request("API 1", lambda: send_post_request(
        url="https://web.udhaar.pk/udhaar/dukaan/create/sendotp/",
        headers={
            "Host": "web.udhaar.pk",
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json; charset=UTF-8"
        },
        json={
            "phone_number": phone_number,
            "referer": None,
            "version": "multi-business"
        }
    ), delay=4))

    tasks.append(handle_api_request("API 2", lambda: send_post_request(
        url="https://staging.cricwick.net:13002/api/send_pin",
        data={
            "telco": "easypaisa",
            "phone": phone_number,
            "sub_type": "",
            "source": 2,
            "sub_source": "CricwickWeb",
            "is_bundle": 1,
            "bundle_id": 13
        }
    ), delay=1))

    tasks.append(handle_api_request("API 3", lambda: send_post_request(
        url="https://jazztv.pk/alpha/api_gateway/index.php/users-dbss/send-otp-wc",
        headers={
            "authorization": "bearer YOUR_BEARER_TOKEN",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "okhttp/3.10.0"
        },
        data={
            "other_telco": "telenor",
            "device_id": "3acc1d874d4538ef",
            "user_id": "58832432",
            "telco": "other",
            "is_jazz_user": "no",
            "mobile": phone_number,
            "type": "prepaid"
        }
    ), delay=3))

    tasks.append(handle_api_request("API 4", lambda: send_post_request(
        url="https://portallapp.com/api/v1/auth/generate-otp",
        json={
            "mobile_no": phone_number[-10:]  # Extract the last 10 digits for mobile_no
        }
    ), delay=1))

    tasks.append(handle_api_request("API 5", lambda: send_post_request(
        url="https://jazztv.pk/alpha/api_gateway/index.php/v2/users-dbss/sign-up-wc",
        headers={
            "Authorization": "bearer YOUR_BEARER_TOKEN",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "okhttp/3.10.0"
        },
        data={
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
    ), delay=1))

    tasks.append(handle_api_request("API 6", lambda: send_post_request(
        url="https://baseapi.oraan.com/api/users/send-otp",
        headers={
            "user-agent": "Dart/2.19 (dart:io)",
            "auth_token": "YOUR_AUTH_TOKEN",
            "accept-encoding": "gzip",
        },
        data={
            "phone": f"+92{phone_number[-10:]}",  # Convert to +92 format for this API
            "whatsapp": "false"
        }
    ), delay=1))

    # Run all tasks concurrently
    results = await asyncio.gather(*tasks)

    # Return the combined results
    return jsonify({"success": True, "responses": results}), 200

if __name__ == '__main__':
    app.run(debug=True)
