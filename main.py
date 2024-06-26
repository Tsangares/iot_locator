from flask import Flask, request, jsonify, redirect
from dotenv import load_dotenv
import os, json, logging
import pytz
from datetime import datetime

# Set the timezone
timezone = pytz.timezone(os.getenv('TIMEZONE','US/Pacific'))

# Load environment variables from .env file
load_dotenv()
VIEW_KEY = os.getenv("VIEW_KEY")
app = Flask(__name__)
DATA_DIR=os.getenv('DATA_DIR','data')

ip_list = []

ip_map = {
    "apple": [ "127.0.0.1" ], 
}
timestamps = {}

@app.route('/ip', methods=['POST'])
def receive_ip():
    data = request.get_json()
    ip = data.get('ip', None)
    namespace = data.get('secret', None)
    if ip:
        current_time = str(datetime.now(timezone))
        if ip not in timestamps:
            timestamps[ip] = [current_time]
        else:
            timestamps[ip].append(current_time)
        if ip not in ip_list:
            ip_list.append(ip)
        if namespace is not None:
            if ip not in ip_map:
                ip_map[namespace] = [ip]
            else:
                ip_map[namespace].append(ip)
        return f"IP {ip} added to the list."
    else:
        return "No IP provided."
    

@app.route('/iplist', methods=['GET'])
def get_ip_list():
    view_key = request.args.get('view_key',None)
    namespace = request.args.get('secret',None)
    if view_key is None or namespace is None or view_key != VIEW_KEY:
        return "Invalid request"
    save_cache()
    if namespace not in ip_map:
        return []
    else:
        return ip_map[namespace]
    
def load_cache():
    global ip_map, ip_list, timestamps
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    cache_file = os.path.join(DATA_DIR, 'cache.json')
    if not os.path.exists(cache_file):
        return
    with open(cache_file, 'r') as f:
        cache = json.load(f)
        ip_map |= cache['map']
        ip_list += cache['list']
        timestamps |= cache['timestamps']

def save_cache():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    cache_file = os.path.join(DATA_DIR, 'cache.json')
    logging.warning(f"Saving cache to {cache_file}")
    with open(cache_file, 'w+') as f:
        json.dump({'map': ip_map, 'list': ip_list, 'timestamps': timestamps}, f)

def get_time_of_ip(ip, relative=False):
    if relative:
        last_time = datetime.strptime(timestamps[ip][-1], "%Y-%m-%d %H:%M:%S.%f%z")
        current_time = datetime.now(timezone)
        delta = current_time - last_time
        return str(delta.total_seconds())
    else:
        return timestamps[ip][-1]

@app.route('/lastseen', methods=['GET'])
def last_seen():
    view_key = request.args.get('view_key', None)
    ip = request.args.get('ip', None)
    namespace = request.args.get('secret', None)
    if view_key is None or view_key != VIEW_KEY:
        return redirect('/')
    if ip not in timestamps or len(timestamps[ip]) == 0:
        if namespace is None: return "IP not found."
    if namespace not in ip_map:
        return "Namespace not found."
    relative = request.args.get('relative', False)
    ips = ip_map[namespace]
    return {ip: get_time_of_ip(ip,relative) for ip in ips}

@app.route('/save', methods=['GET'])
def save_endpoint():
    view_key = request.args.get('view_key',None)
    if view_key is None or view_key != VIEW_KEY:
        return redirect('/')

if __name__ == '__main__':
    params = {
        'host': str(os.getenv('HOST','localhost')),
        'port': int(os.getenv('PORT',8888)),
        'debug': bool(os.getenv('DEBUG',False))
    }
    load_cache()
    app.run(**params)
