# Functions for interacting with the Large Language Model

import chess
import chess.engine
import ollama
import os

# --- Stockfish Configuration --- #
# Try to find Stockfish automatically, otherwise specify the path.
# Replace with the actual path if needed, e.g., "/usr/local/bin/stockfish"
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "stockfish") 

# Initialize Stockfish engine (lazily)
engine = None
def get_stockfish_engine():
    global engine
    if engine is None:
        try:
            engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        except FileNotFoundError:
            print(f"!!! STOCKFISH ENGINE NOT FOUND at {STOCKFISH_PATH} !!!")
            print("Please install Stockfish or set the STOCKFISH_PATH environment variable.")
            engine = None # Ensure it stays None if not found
        except Exception as e:
            print(f"Error initializing Stockfish: {e}")
            engine = None
    return engine

# --- LLM Integration --- #

def get_coach_advice(fen_string, user_query):
    """Gets analysis from Stockfish and uses Llama 3 via Ollama for coaching."""
    
    stockfish_engine = get_stockfish_engine()
    stockfish_analysis = "Stockfish analysis not available."
    best_move = "N/A"
    score = "N/A"

    if stockfish_engine:
        try:
            board = chess.Board(fen_string)
            # Analyze for 1 second (adjust time as needed)
            info = stockfish_engine.analyse(board, chess.engine.Limit(time=1.0))
            
            best_move_uci = info.get("pv")[0].uci() if info.get("pv") else "(no pv)"
            score_cp = info.get("score").relative.score(mate_score=10000) if info.get("score") else "(no score)"
            score = f"{score_cp / 100.0:.2f}" # Convert centipawns to pawns
            best_move = best_move_uci

            # Use a single triple-quoted f-string for multiline clarity
            stockfish_analysis = f"""Stockfish Analysis (depth {info.get('depth', 'N/A')}):
- Best move found: {best_move_uci}
- Position evaluation: {score} (positive is good for White, negative for Black)
- Principal variation (PV): {' '.join(m.uci() for m in info.get('pv', []))}"""
            
            print(f"Stockfish analysis result: {stockfish_analysis}") # Log analysis
        except Exception as e:
            print(f"Error during Stockfish analysis: {e}")
            stockfish_analysis = f"Error analyzing position with Stockfish: {e}"
    else:
         print("Stockfish engine not available for analysis.")

    # --- Prepare Prompt for Llama 3 --- #
    prompt = f"""
You are an AI Chess Coach. You are talking to a student during a game.
The current chess board state is given by this FEN string: {fen_string}

Stockfish analysis of the current position:
{stockfish_analysis}

The student asks: "{user_query}"

Provide helpful, encouraging, and concise advice to the student based on their question and the Stockfish analysis. Explain the reasoning simply. Focus on the *why* behind good moves or ideas, not just naming the best move unless specifically asked. If Stockfish isn't available, answer based on the board state and general principles.
Coach's Advice:"""

    print(f"\n--- Sending prompt to Llama 3 ---\n{prompt}\n---------------------------------")

    # --- Call Llama 3 via Ollama --- #
    try:
        response = ollama.chat(
            model='llama3', 
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        advice = response['message']['content']
        print(f"Llama 3 response: {advice}") # Log response
        return advice.strip()
    except Exception as e:
        print(f"Error calling Ollama/Llama 3: {e}")
        return f"Sorry, I encountered an error trying to reach the AI coach ({e}). Stockfish analysis was: {best_move}, {score}"

# --- Engine Cleanup --- #
def close_engine():
    global engine
    if engine:
        print("Closing Stockfish engine...")
        engine.quit()
        engine = None 