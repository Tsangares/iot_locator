from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
VIEW_KEY = os.getenv("VIEW_KEY")
app = Flask(__name__)

ip_list = []

ip_map = {
    "apple": [ "127.0.0.1" ], 
}

@app.route('/ip', methods=['POST'])
def receive_ip():
    data = request.get_json()
    ip = data.get('ip',None)
    secret = data.get('secret', None)
    if ip:
        ip_list.append(ip)
        if secret is not None and ip not in ip_map[secret]:
            ip_map[secret] = ip
        return f"IP {ip} added to the list."
    else:
        return "No IP provided."
    

@app.route('/iplist', methods=['GET'])
def get_ip_list():
    view_key = request.args.get('view_key',None)
    secret = request.args.get('secret',None)
    if view_key is None or secret is None or view_key != VIEW_KEY:
        return "Invalid request"
    if secret not in ip_map:
        return []
    else:
        return ip_map[secret]
    

if __name__ == '__main__':
    params = {
        'host': str(os.getenv('HOST','localhost')),
        'port': int(os.getenv('PORT',8888)),
        'debug': bool(os.getenv('DEBUG',False))
    }
    app.run(**params)
