from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexigraph_py.game import LexigraphGame

app = Flask(__name__, static_folder='static')
socketio = SocketIO(app, cors_allowed_origins="*")

game = LexigraphGame()

@app.route('/')
def index():
    return send_from_directory('static/controller', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static/controller', path)

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    # Send current state immediately on connect
    emit('state_update', {'grid': game.grid.serialize()})

@socketio.on('join_game')
def handle_join(name):
    player = game.add_player(request.sid, name)
    print(f"Player joined: {name} ({player.color})")
    emit('player_joined', {'id': player.id, 'name': player.name, 'color': player.color}, broadcast=True)
    # Broadcast full state update to everyone
    emit('state_update', {'grid': game.grid.serialize()}, broadcast=True)

@socketio.on('submit_move')
def handle_move(coords):
    print(f"Move received from {request.sid}: {coords}")
    result = game.process_move(request.sid, coords)
    
    emit('move_result', result)
    
    if result['success']:
        # Broadcast grid update to everyone
        emit('state_update', {'grid': game.grid.serialize()}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    game.remove_player(request.sid)
    emit('state_update', {'grid': game.grid.serialize()}, broadcast=True)

def run_server(port=3000):
    socketio.run(app, host='0.0.0.0', port=port)

if __name__ == '__main__':
    run_server()
