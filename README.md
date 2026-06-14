Hand Gesture Tic Tac Toe
by Sidharth Praveen

A Python-based Tic Tac Toe game controlled entirely through hand gestures via webcam.
Play against an AI opponent in real time — no keyboard or mouse needed.

────────────────────────────────────────────
 Features
────────────────────────────────────────────
- Hand gesture controls using your webcam
- AI opponent powered by Minimax with Alpha-Beta Pruning
- 3 difficulty levels: Easy, Medium, and Hard
- Smooth animations — pieces fade in, win line draws itself
- Live score tracker (You vs AI vs Draws)
- Hover highlight shows which cell you're pointing at
- AI "thinking" indicator before each move
- Ghost camera blended into dark background
- 1280x720 widescreen layout with side panels

────────────────────────────────────────────
 Gestures
────────────────────────────────────────────
Index finger   ->  Place your move (X)
Peace sign     ->  Cycle difficulty (Easy / Medium / Hard)
Open palm      ->  Reset the game

────────────────────────────────────────────
 Technologies Used
────────────────────────────────────────────
- Python
- OpenCV
- cvzone
- MediaPipe
- NumPy

────────────────────────────────────────────
 Installation
────────────────────────────────────────────
1. Clone the repository
2. Create a virtual environment (recommended):

   python -m venv venv
   venv\Scripts\activate        (Windows)
   source venv/bin/activate     (Mac/Linux)

3. Install dependencies:

   pip install -r requirements.txt

────────────────────────────────────────────
 Run
────────────────────────────────────────────
   python gesture_tictactoe.py

Press ESC to quit.

────────────────────────────────────────────
 Notes
────────────────────────────────────────────
- Make sure your webcam is enabled
- Close other apps using the camera before running
- Hard mode uses perfect Minimax — it cannot be beaten, only drawn
