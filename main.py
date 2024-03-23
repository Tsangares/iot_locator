from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

SECRET = os.getenv('SECRET', "apple")


app = Flask(__name__)

ip_list = []

@app.route('/ip', methods=['POST'])
def receive_ip():
    data = request.get_json()
    ip = data.get('ip',None)
    secret = data.get('secret', None)
    if secret != SECRET:
        return "Invalid request"
    #print(ip, secret)
    if ip:
        ip_list.append(ip)
        return f"IP {ip} added to the list."
    else:
        return "No IP provided."

@app.route('/iplist', methods=['GET'])
def get_ip_list():
    secret = request.args.get('secret',None)
    if secret != SECRET:
        return "Invalid request"
    return ', '.join(list(set(ip_list)))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6086)
