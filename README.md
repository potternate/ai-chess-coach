# AI Chess Coach

## Overview
Welcome to the AI Chess Coach! This application leverages advanced AI to provide real-time coaching and analysis for chess players of all levels. Whether you're a beginner or a seasoned pro, our app is designed to help you improve your game.

## Features
- **Real-time Chess Analysis**: Get instant feedback on your moves using the Stockfish engine.
- **AI Coaching**: Receive personalized advice from Llama 3 based on your game state.
- **Interactive Chat Interface**: Ask questions and get responses in a conversational format.
- **Modern UI/UX**: Enjoy a sleek, user-friendly interface that enhances your chess experience.

## Getting Started

### Prerequisites
- Python 3.x
- Stockfish chess engine
- Ollama for Llama 3 integration

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/chesscoach.git
   cd chesscoach
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the Stockfish path:
   - Ensure Stockfish is installed and accessible. You can set the path in your environment variables or directly in the code.

### Running the Application
To start the Flask app, run:
```bash
python main.py
```
Open your browser and navigate to `http://127.0.0.1:5001` to access the app.

## Usage
- **Ask the Coach**: Type your question about the current position in the chat box and hit "Ask" to receive coaching advice.
- **Chessboard Interaction**: Move pieces on the board and see real-time analysis.

## Contributing
We welcome contributions! If you have suggestions or improvements, feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Thanks to the developers of Stockfish and Llama 3 for their amazing work in AI and chess analysis.