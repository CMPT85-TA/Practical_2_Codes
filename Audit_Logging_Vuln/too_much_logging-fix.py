from flask import Flask, request
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.route('/make_purchase', methods=['POST'])
def purchase():
    data = request.get_json()
    cc_number_last4 = data.get('cc_number', '')[-4:]
    if 'cc_number' not in data.keys():
        return "<html><body>Missing cc_number</body></html>"
    logging.error(f'Customer made a purchase with missing cc_number: *************-{cc_number_last4}')
    return f"<html><body>Thank you for the purchase!</body></html>"
    

app.run(port=5000)
