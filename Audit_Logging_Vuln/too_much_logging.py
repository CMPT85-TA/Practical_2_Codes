from flask import Flask, request
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.route('/make_purchase', methods=['POST'])
def purchase():
    data = request.get_json()
    if 'cc_number' not in data.keys():
        return "<html><body>Missing cc_number</body></html>"
    logging.error(f'Customer made a purchase with CC number {data["cc_number"]}')
    return f"<html><body>Thank you for the purchase!</body></html>"
    

app.run(port=5000)
