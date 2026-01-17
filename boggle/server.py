from flask import Flask, jsonify, request, render_template_string
import threading
import time
from game_state import BoggleGame
import logging

# Disable flask startup banner
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
game = BoggleGame()

# Add some dummy players for demo
game.add_player("MVB")
game.add_player("Guest")

@app.route('/state')
def get_state():
    # Trigger timer update side-effects
    game.get_time_remaining() 
    return jsonify(game.to_json())

@app.route('/start', methods=['POST'])
def start_game():
    game.start_game()
    return jsonify({"status": "started"})

@app.route('/reset', methods=['POST'])
def reset_game():
    game.state = "LOBBY"
    game.players = {} # clear players?
    game.add_player("MVB") # restore host
    return jsonify({"status": "reset"})

@app.route('/join', methods=['POST'])
def join():
    data = request.json
    name = data.get('name')
    if name:
        game.add_player(name)
        return jsonify({"status": "joined", "name": name})
    return jsonify({"error": "no name"}), 400

# Components Rendering (HTML for the windows)

@app.route('/view/board')
def view_board():
    # Auto-refreshing HTML page wrapper around the SVG
    html_head = """
    <html>
    <head>
        <meta http-equiv="refresh" content="1">
        <style>
            body { 
                background-color: #1e1e2e; 
                margin: 0; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                overflow: hidden; 
            }
            .waiting { font-family: sans-serif; font-size: 3rem; color: #89b4fa; font-weight: bold; }
        </style>
    </head>
    <body>
    """
    
    if game.state == 'PLAYING' or game.state == 'SCORING':
        content = game.to_svg()
    else:
        content = """
        <div class="waiting">
            Waiting for Start...
        </div>
        """
        
    return html_head + content + "</body></html>"


@app.route('/view/timer')
def view_timer():
    html = """
    <html>
    <head>
        <meta http-equiv="refresh" content="0.5">
        <style>
            body { background-color: #1e1e2e; color: #fab387; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; }
            .timer { font-size: 8rem; font-weight: bold; }
            .sc-state { font-size: 3rem; color: #a6e3a1; }
        </style>
    </head>
    <body>
        {% if state == 'PLAYING' %}
            <div class="timer">{{ time }}</div>
        {% else %}
            <div class="sc-state">{{ state }}</div>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html, state=game.state, time=game.get_time_remaining())

@app.route('/view/leaderboard')
def view_leaderboard():
    html = """
    <html>
    <head>
        <meta http-equiv="refresh" content="2">
        <style>
            body { background-color: #1e1e2e; color: #cdd6f4; font-family: sans-serif; padding: 20px; }
            h1 { color: #f9e2af; text-align: center; border-bottom: 2px solid #45475a; padding-bottom: 10px; }
            .player { display: flex; justify-content: space-between; font-size: 1.5rem; padding: 10px; border-bottom: 1px solid #313244; }
            .score { font-weight: bold; color: #a6e3a1; }
        </style>
    </head>
    <body>
        <h1>LEADERBOARD</h1>
        <div class="list">
            {% for p in players|sort(attribute='score', reverse=True) %}
            <div class="player">
                <span>{{ p.name }}</span>
                <span class="score">{{ p.score }}</span>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html, players=game.players.values())

@app.route('/view/join')
def view_join():
    html = """
    <html>
    <head>
        <style>
            body { 
                background-color: #1e1e2e; 
                color: #89b4fa; 
                font-family: sans-serif; 
                margin: 0; 
                height: 100vh; 
                overflow: hidden;
                position: relative;
            }
            .content {
                position: absolute;
                bottom: 20px;
                right: 20px;
                display: flex;
                flex-direction: row;
                align-items: center;
                gap: 20px;
                background: rgba(30, 30, 46, 0.9);
                padding: 15px;
                border-radius: 12px;
                border: 1px solid #45475a;
            }
            h2 { margin: 0; font-size: 1.5rem; text-align: right; }
            p { margin: 5px 0 0 0; font-size: 1.2rem; color: #cdd6f4; font-family: monospace; }
            .code { background: white; padding: 10px; border-radius: 8px; line-height: 0; }
            .text-block { text-align: right; }
        </style>
    </head>
    <body>
        <div class="content">
            <div class="text-block">
                <h2>JOIN GAME</h2>
                <p>http://192.168.1.31:8080/controller</p>
            </div>
            <div class="code">
                <!-- Placeholder for QR -->
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=http://192.168.1.31:8080/controller" />
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/submit', methods=['POST'])
def submit_word():
    data = request.json
    name = data.get('name')
    word = data.get('word')
    if name and word:
        success = game.submit_word(name, word)
        return jsonify({"status": "submitted", "accepted": success, "word": word})
    return jsonify({"error": "missing data"}), 400

@app.route('/controller')
def view_controller():
    # Simple mobile controller
    html = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { background-color: #11111b; color: #cdd6f4; font-family: sans-serif; padding: 20px; text-align: center; }
            button { background: #89b4fa; border: none; padding: 15px 30px; font-size: 1.2rem; border-radius: 8px; margin: 10px; width: 100%; cursor: pointer; color: #1e1e2e; font-weight: bold; }
            input { padding: 15px; font-size: 1.2rem; width: 100%; margin-bottom: 10px; border-radius: 8px; border: none; }
            .admin { margin-top: 30px; border-top: 1px solid #313244; padding-top: 20px; }
            .btn-start { background: #a6e3a1; }
        </style>
    </head>
    <body>
        <h1>Boggle Controller</h1>
        
        <div id="join-section">
            <input type="text" id="pname" placeholder="Enter Name">
            <button onclick="join()">Join Game</button>
        </div>

        <div id="game-section" style="display:none;">
            <h2 id="welcome"></h2>
            <input type="text" id="word" placeholder="Type word...">
            <button onclick="submitWord()">Submit Word</button>
        </div>

        <div class="admin">
            <h3>Admin Controls</h3>
            <button class="btn-start" onclick="fetch('/start', {method: 'POST'})">START GAME</button>
            <button onclick="fetch('/reset', {method: 'POST'})">RESET</button>
        </div>

        <script>
            let myName = "";
            function join() {
                myName = document.getElementById('pname').value;
                if(!myName) return;
                
                fetch('/join', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: myName})
                })
                .then(r => r.json())
                .then(d => {
                    document.getElementById('join-section').style.display = 'none';
                    document.getElementById('game-section').style.display = 'block';
                    document.getElementById('welcome').innerText = "Player: " + myName;
                });
            }
            
            function submitWord() {
                let w = document.getElementById('word').value;
                if(!w) return;
                
                fetch('/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: myName, word: w})
                })
                .then(r => r.json())
                .then(d => {
                    let msg = d.accepted ? "Accepted!" : "Rejected (Duplicate/Short)";
                    // Show simple feedback
                    let btn = document.querySelector('#game-section button');
                    let oldText = btn.innerText;
                    btn.innerText = msg;
                    setTimeout(() => btn.innerText = oldText, 1000);
                    
                    document.getElementById('word').value = "";
                });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

def run_server():
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

if __name__ == "__main__":
    run_server()
