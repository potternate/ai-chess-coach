// NOTE: this example uses the chess.js library: https://github.com/jhlywa/chess.js
// and the chessboard.js library: https://github.com/oakmac/chessboardjs/

var board = null; // Will hold the chessboard.js instance
var game = new Chess(); // Will hold the chess.js instance
var $status = $('#status'); // jQuery object for status element

function onDragStart (source, piece, position, orientation) {
  // do not pick up pieces if the game is over
  if (game.game_over()) return false;

  // only pick up pieces for the side to move
  if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
      (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
    return false;
  }
}

function onDrop (source, target) {
  // see if the move is legal
  var move = game.move({
    from: source,
    to: target,
    promotion: 'q' // NOTE: always promote to a queen for example simplicity
  });

  // illegal move
  if (move === null) return 'snapback';

  // move is legal, send it to the backend
  sendMoveToServer(move.from, move.to, move.promotion);
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
  board.position(game.fen());
}

function updateStatus () {
  var status = '';

  var moveColor = 'White';
  if (game.turn() === 'b') {
    moveColor = 'Black';
  }

  // checkmate?
  if (game.in_checkmate()) {
    status = 'Game over, ' + moveColor + ' is in checkmate.';
  }

  // draw?
  else if (game.in_draw()) {
    status = 'Game over, drawn position';
  }

  // game still on
  else {
    status = moveColor + ' to move';

    // check?
    if (game.in_check()) {
      status += ', ' + moveColor + ' is in check';
    }
  }

  $status.html(status);
}

// Function to send the move to the Flask backend
function sendMoveToServer(source, target, promotion) {
    fetch('/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            move_uci: source + target + (promotion ? promotion : '') 
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // If backend confirms, update chess.js game state and chessboard.js UI
            game.load(data.fen); // Load new FEN from backend
            board.position(data.fen);
            updateStatus();
            // maybe display flashed message from server?
            if(data.message) {
              // crude way to add server messages to status for now
              $status.html($status.html() + `<br><span class='server-message'>${data.message}</span>`);
            }
        } else {
            // Move was invalid according to backend, revert UI move
            console.error("Backend rejected move:", data.error);
            // Reload the previous state to be safe
            game.load(data.fen || board.fen()); // Use FEN from server if available
            board.position(game.fen());
            alert("Invalid move: " + (data.error || "Rejected by server"));
        }
    })
    .catch((error) => {
        console.error('Error sending move:', error);
        // Revert board on error
        game.undo(); // Undo the move in chess.js
        board.position(game.fen()); // Update the UI
        alert("Error communicating with server.");
    });
}

$(document).ready(function() {
    // Initialize the board only after the DOM is ready
    var config = {
      draggable: true,
      position: initialFen || 'start', // Use FEN from Flask or default
      pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
      onDragStart: onDragStart,
      onDrop: onDrop,
      onSnapEnd: onSnapEnd
    };
    board = Chessboard('myBoard', config);

    // Load the initial FEN into chess.js as well
    if (typeof initialFen !== 'undefined' && initialFen) {
        game.load(initialFen);
    } else {
        // Fallback if initialFen isn't set for some reason
        game.load('start'); 
        console.warn("Initial FEN not provided, starting default board.")
    }

    updateStatus(); 

    // --- Event listener for the Ask Coach button ---
    $('#ask-button').on('click', function() {
        var userQuery = $('#user-query').val();
        var $adviceDiv = $('#coach-advice');
        
        if (!userQuery.trim()) {
            $adviceDiv.text("Please enter a question first.");
            return;
        }

        $adviceDiv.text("Asking the coach..."); // Show loading state

        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                query: userQuery 
                // FEN is read server-side from the global board object
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display the coach's advice
                $adviceDiv.text(data.advice);
            } else {
                // Display error message
                $adviceDiv.text("Error: " + (data.error || "Unknown error from coach."));
                console.error("Error asking coach:", data.error);
            }
        })
        .catch((error) => {
            console.error('Error asking coach:', error);
            $adviceDiv.text("Error communicating with the coach server.");
        });
    });
});

// Make sure initialFen is defined globally if needed elsewhere, 
// or ideally pass it into the ready function if possible.
// (It's currently defined via a <script> tag in the HTML before this file is loaded) 