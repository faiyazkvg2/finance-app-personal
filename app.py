import os
from flask import Flask, render_template, jsonify, request, session
from flask_talisman import Talisman

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_prod')

# Security Headers
csp = {
    'default-src': '\'self\'',
    'script-src': '\'self\'',
    'style-src': '\'self\'',
}
Talisman(app, content_security_policy=csp, force_https=False)  # force_https=False for local dev


def check_winner(board):
    # Winning combinations
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]

    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] and board[combo[0]] != "":
            return board[combo[0]]

    if "" not in board:
        return "Draw"

    return None


@app.route('/')
def index():
    if 'board' not in session:
        reset_game_state()
    return render_template('index.html')


@app.route('/move', methods=['POST'])
def move():
    if 'board' not in session:
        reset_game_state()

    board = session['board']
    current_player = session['current_player']
    game_over = session['game_over']

    if game_over:
        return jsonify({'status': 'error', 'message': 'Game is over'}), 400

    data = request.get_json()
    index = data.get('index')

    if index is None or not (0 <= index < 9):
        return jsonify({'status': 'error', 'message': 'Invalid move'}), 400

    if board[index] != "":
        return jsonify({'status': 'error', 'message': 'Cell already taken'}), 400

    board[index] = current_player

    winner = None
    result = check_winner(board)
    if result:
        game_over = True
        winner = result
    else:
        current_player = "O" if current_player == "X" else "X"

    # Update session
    session['board'] = board
    session['current_player'] = current_player
    session['game_over'] = game_over
    session['winner'] = winner

    return jsonify({
        'board': board,
        'current_player': current_player,
        'winner': winner,
        'game_over': game_over
    })


@app.route('/reset', methods=['POST'])
def reset():
    reset_game_state()
    return jsonify({
        'board': session['board'],
        'current_player': session['current_player'],
        'winner': session['winner'],
        'game_over': session['game_over']
    })


def reset_game_state():
    session['board'] = [""] * 9
    session['current_player'] = "X"
    session['winner'] = None
    session['game_over'] = False


if __name__ == '__main__':
    app.run(debug=True)
