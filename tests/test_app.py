import pytest
import json
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_game_state(client):
    # Reset game state before each test by calling reset endpoint
    # This ensures the session is fresh for the test client
    client.post('/reset')


def test_index_route(client):
    """Test that the index page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Tic Tac Toe" in response.data


def test_initial_state(client):
    """Test the initial state of the game after reset."""
    response = client.post('/reset')
    data = json.loads(response.data)
    assert data['board'] == [""] * 9
    assert data['current_player'] == "X"
    assert data['winner'] is None
    assert data['game_over'] is False


def test_make_move(client):
    """Test making a valid move."""
    response = client.post('/move', json={'index': 0})
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['board'][0] == "X"
    assert data['current_player'] == "O"


def test_invalid_move_taken(client):
    """Test making a move on an already taken cell."""
    client.post('/move', json={'index': 0})  # X moves
    response = client.post('/move', json={'index': 0})  # O tries to move same spot
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['message'] == "Cell already taken"


def test_invalid_move_out_of_bounds(client):
    """Test making a move with an invalid index."""
    response = client.post('/move', json={'index': 9})
    assert response.status_code == 400

    response = client.post('/move', json={'index': -1})
    assert response.status_code == 400


def test_win_condition_row(client):
    """Test winning by a row."""
    # X wins top row
    moves = [0, 3, 1, 4, 2]
    # X:0, O:3, X:1, O:4, X:2

    for move in moves:
        client.post('/move', json={'index': move})

    # Re-simulating to capture last response
    client.post('/reset')
    client.post('/move', json={'index': 0})  # X
    client.post('/move', json={'index': 3})  # O
    client.post('/move', json={'index': 1})  # X
    client.post('/move', json={'index': 4})  # O
    response = client.post('/move', json={'index': 2})  # X wins

    data = json.loads(response.data)
    assert data['winner'] == "X"
    assert data['game_over'] is True


def test_draw_condition(client):
    """Test a draw condition."""
    # X O X
    # X O X
    # O X O
    # 0, 1, 2 (X, O, X)
    # 4, 3, 5 (O, X, O)
    # 7, 8, 6 (X, O, X) -> Draw

    client.post('/reset')
    client.post('/move', json={'index': 0})  # X
    client.post('/move', json={'index': 1})  # O
    client.post('/move', json={'index': 2})  # X

    client.post('/move', json={'index': 4})  # O
    client.post('/move', json={'index': 3})  # X
    client.post('/move', json={'index': 5})  # O

    client.post('/move', json={'index': 7})  # X
    client.post('/move', json={'index': 6})  # O
    response = client.post('/move', json={'index': 8})  # X

    data = json.loads(response.data)
    assert data['winner'] == "Draw"
    assert data['game_over'] is True


def test_move_after_game_over(client):
    """Test making a move after the game is over."""
    # X wins
    client.post('/move', json={'index': 0})
    client.post('/move', json={'index': 3})
    client.post('/move', json={'index': 1})
    client.post('/move', json={'index': 4})
    client.post('/move', json={'index': 2})

    # Try to move again
    response = client.post('/move', json={'index': 8})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['message'] == "Game is over"
