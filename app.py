from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
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
                if response.status != 200:
                    logger.error(f"Request failed: {response.status} - {await response.text()}")
                    return {"status": response.status, "error": await response.text()}
                response_data = await response.json()
                logger.info(f"Request to {url} succeeded with status {response.status}")
                return {"status": response.status, "response": response_data}
        except Exception as e:
            logger.error(f"Request to {url} failed: {e}")
            return {"error": str(e)}

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

    # Testing with just one API request to isolate the issue
    result = await send_post_request(
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
    )

    # Return the result of the single request
    if "error" in result:
        return jsonify({"error": f"API request failed: {result['error']}"}), result.get("status", 500)
    else:
        return jsonify({"success": True, "response": result["response"]}), 200

if __name__ == '__main__':
    app.run(debug=True)
