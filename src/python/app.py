from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)
port = int(os.environ.get('PORT', 8000))

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'python'
    }), 200

@app.route('/ready')
def ready():
    return jsonify({
        'status': 'ready',
        'service': 'python'
    }), 200

@app.route('/')
def hello():
    return jsonify({
        'message': 'Hello from Python Application!',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)