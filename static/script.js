document.addEventListener('DOMContentLoaded', () => {
    const boardElement = document.getElementById('board');
    const statusElement = document.getElementById('status');
    const resetBtn = document.getElementById('reset-btn');
    const cells = document.querySelectorAll('.cell');

    let gameOver = false;

    // Initialize board
    fetchState();

    cells.forEach(cell => {
        cell.addEventListener('click', () => {
            if (gameOver || cell.classList.contains('taken')) return;

            const index = cell.dataset.index;
            makeMove(parseInt(index));
        });
    });

    resetBtn.addEventListener('click', resetGame);

    function makeMove(index) {
        fetch('/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ index: index }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'error') {
                    alert(data.message);
                } else {
                    updateBoard(data);
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function resetGame() {
        fetch('/reset', {
            method: 'POST',
        })
            .then(response => response.json())
            .then(data => {
                updateBoard(data);
            })
            .catch(error => console.error('Error:', error));
    }

    function fetchState() {
        // In a real app we might want a GET /state endpoint, 
        // but for now reset gives us a clean state or we could just rely on initial load.
        // However, since the server holds state, if we refresh, we should probably know the state.
        // For simplicity in this version, we'll just start fresh or let the user play.
        // If we wanted persistence across refresh without a DB, we'd need a GET endpoint.
        // Let's just reset on load for a clean start or assume empty.
        // Actually, let's add a simple GET /state to app.py if we wanted to be robust, 
        // but the plan didn't specify it. I'll stick to the plan.
        // Wait, if I refresh the page, the python variable `board` is still in memory!
        // So the HTML will render empty (because of the loop in jinja just making divs), 
        // but the server thinks the board has moves.
        // I should probably fetch the state on load.
        // Let's add a small GET endpoint to app.py or just use reset on load?
        // Reset on load is annoying if you accidentally refresh.
        // I'll add a GET /state endpoint to app.py in a subsequent step if needed, 
        // but for now let's just use reset on load to be safe, OR just implement the UI update 
        // to handle the visual sync if I were to add that.
        // Actually, the simplest way to sync is to have the index route pass the board state 
        // to the template, and the template render it.
        // My current index.html just renders empty divs.
        // Let's stick to the current plan: The JS starts, the board is visually empty. 
        // If the server has state, we might get "Cell taken" errors.
        // I will add a `resetGame()` call on load to ensure sync for this simple version.
        resetGame();
    }

    function updateBoard(data) {
        const board = data.board;
        const currentPlayer = data.current_player;
        const winner = data.winner;
        gameOver = data.game_over;

        cells.forEach((cell, index) => {
            cell.textContent = board[index];
            cell.className = 'cell'; // Reset classes
            if (board[index] !== "") {
                cell.classList.add('taken');
                cell.classList.add(board[index].toLowerCase());
            }
        });

        if (winner) {
            if (winner === 'Draw') {
                statusElement.textContent = "It's a Draw!";
            } else {
                statusElement.textContent = `Player ${winner} Wins!`;
            }
        } else {
            statusElement.textContent = `Current Player: ${currentPlayer}`;
        }
    }
});
