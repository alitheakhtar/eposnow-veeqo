import requests
from flask import Flask, request, jsonify
import threading
import time

# Initialize the Flask app
app = Flask(__name__)

# Define your API keys for Veeqo and EPOS Now
VEEQO_API_KEY = 'your-veeqo-api-key'
EPOSNOW_API_KEY = 'your-eposnow-api-key'

def poll_veeqo():
    """Poll Veeqo for stock updates in a loop."""
    while True:
        sync_veeqo_to_eposnow()
        time.sleep(60*5)  # Poll every 5 minutes

def sync_veeqo_to_eposnow():
    """Fetch all products from Veeqo and update stock levels in EPOS Now."""
    veeqo_products = get_veeqo_products()
    for product in veeqo_products:
        product_id = product.get('product_id')
        stock_level = product.get('stock_level')
        update_eposnow_stock(EPOSNOW_API_KEY, product_id, stock_level)

def get_veeqo_products():
    """Fetch all products from Veeqo."""
    url = "https://api.veeqo.com/products"
    headers = {'x-api-key': VEEQO_API_KEY}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

@app.route('/eposnow-webhook', methods=['POST'])
def eposnow_webhook():
    """Handle webhook notifications from EPOS Now."""
    sync_all_products()
    return jsonify(status='success'), 200

def sync_all_products():
    """Fetch all products from EPOS Now and update stock levels in Veeqo."""
    eposnow_products = get_eposnow_products()
    for product in eposnow_products:
        product_id = product.get('product_id')
        stock_level = product.get('stock_level')
        update_veeqo_stock(VEEQO_API_KEY, product_id, stock_level)

def get_eposnow_products():
    """Fetch all products from EPOS Now."""
    url = "https://api.eposnowhq.com/api/V2/product"
    headers = {'Authorization': 'Bearer your-eposnow-api-key'}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

def update_veeqo_stock(api_key, product_id, stock_level):
    """Update stock levels in Veeqo for a specific product."""
    url = f"https://api.veeqo.com/products/{product_id}/stock_levels"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }
    payload = {
        'stock_level': stock_level
    }
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Failed to update Veeqo stock for product {product_id}: {response.status_code}")

def update_eposnow_stock(api_key, product_id, stock_level):
    """Update stock levels in EPOS Now for a specific product."""
    url = f"https://api.eposnowhq.com/api/V2/Product/{product_id}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    payload = {
        'StockLevel': stock_level
    }
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Failed to update EPOS Now stock for product {product_id}: {response.status_code}")

if __name__ == '__main__':
    # Start the Veeqo polling thread
    polling_thread = threading.Thread(target=poll_veeqo)
    polling_thread.start()
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
