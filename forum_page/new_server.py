from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace-this-with-a-real-secret'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):
    # broadcast incoming messages to all connected clients
    send(msg, broadcast=True)

if __name__ == '__main__':
    # listen on all interfaces so LAN clients can connect
    socketio.run(app, host='192.168.0.83', port=5000)
