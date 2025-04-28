from flask import Flask, render_template, jsonify, request
import chess
# import chess.svg # No longer needed for main display
from chess_logic import initialize_board
from llm_integration import get_coach_advice, close_engine # Import close_engine
import atexit # Import atexit
# import os # No longer needed for flash secret key

app = Flask(__name__)
# app.secret_key = os.urandom(24) # Not needed if not using flash

# Initialize the board globally 
board = initialize_board()

@app.route('/')
def home():
    # Pass the current board state (FEN string) to the template
    initial_fen = board.fen()
    return render_template('index.html', initial_fen=initial_fen)

@app.route('/move', methods=['POST'])
def make_move():
    data = request.get_json()
    move_uci = data.get('move_uci')
    current_fen = board.fen() # Get FEN before attempting move
    message = None

    if not move_uci:
        return jsonify({"success": False, "error": "No move provided.", "fen": current_fen})

    try:
        move = board.parse_uci(move_uci)
        if move in board.legal_moves:
            board.push(move)
            new_fen = board.fen()
            # Check game status after the move
            if board.is_checkmate():
                message = f"Checkmate! {'Black' if board.turn == chess.WHITE else 'White'} wins."
            elif board.is_stalemate():
                message = "Stalemate! It's a draw."
            elif board.is_insufficient_material():
                message = "Draw due to insufficient material."
            elif board.is_seventyfive_moves():
                message = "Draw due to 75-move rule."
            elif board.is_fivefold_repetition():
                message = "Draw due to fivefold repetition."
            elif board.is_check():
                message = "Check!"
            return jsonify({"success": True, "fen": new_fen, "message": message})
        else:
            return jsonify({"success": False, "error": f"Invalid move: {move_uci}", "fen": current_fen})
    except ValueError:
        return jsonify({"success": False, "error": f"Invalid move format: {move_uci}. Use UCI notation.", "fen": current_fen})
    except Exception as e:
        print(f"Error processing move: {e}") # Log the error server-side
        return jsonify({"success": False, "error": "An internal error occurred.", "fen": current_fen})

@app.route('/ask', methods=['POST'])
def ask_coach():
    data = request.get_json()
    user_query = data.get('query')
    current_fen = board.fen() # Get the board state when the question is asked

    if not user_query:
        return jsonify({"success": False, "error": "No query provided."})
    
    try:
        # Call the placeholder LLM function
        advice = get_coach_advice(current_fen, user_query)
        return jsonify({"success": True, "advice": advice})
    except Exception as e:
        print(f"Error getting advice: {e}") # Log the error
        return jsonify({"success": False, "error": "Failed to get advice from the coach."})

# No longer need the SVG endpoint
# @app.route('/board.svg')
# def get_board_svg():
#     return jsonify(svg=chess.svg.board(board=board))

# Register the cleanup function to run when the application exits
atexit.register(close_engine)

if __name__ == "__main__":
    print("Starting AI Chess Coach web server...")
    app.run(debug=True, host='0.0.0.0', port=5001)
    # Main logic goes here 