from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    phone_number = data.get('phone_number')
    if not phone_number:
        logger.error("No phone number provided in the request.")
        return jsonify({"error": "Phone number is required"}), 400

    logger.info(f"Sending OTP to phone number: {phone_number}")

    try:
        # Make a sample API request
        response = requests.post(
            "https://web.udhaar.pk/udhaar/dukaan/create/sendotp/",
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
        # Check if the request was successful
        if response.status_code != 200:
            logger.error(f"API request failed with status {response.status_code}: {response.text}")
            return jsonify({"error": f"API request failed: {response.status_code}"}), response.status_code

        logger.info(f"OTP sent successfully. Response: {response.json()}")
        return jsonify({"success": True, "response": response.json()}), 200

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
