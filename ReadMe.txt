Hand Gesture Tic Tac Toe

This is a Python-based Tic Tac Toe game controlled using hand gestures through a webcam. The project uses computer vision techniques to detect hand movements and allows the user to play against an AI opponent in real time.

Features
- Hand gesture-based gameplay using webcam  
- AI opponent using Minimax algorithm  
- Real-time interaction and visual feedback  
- Reset game using open palm gesture  

Technologies Used
- Python  
- OpenCV  
- cvzone  
- MediaPipe  
- NumPy  

. Installation

-Install required libraries:

pip install -r requirements.txt

. Run the Project

python gesture_tictactoe.py

How It Works
The system captures video input from the webcam and detects hand landmarks using a hand tracking module. The position of the index finger is used to select grid cells. The game logic is handled using a Minimax-based AI, which plays optimally against the user.


- Make sure your webcam is enabled  
- Close other applications using the camera before running the project  


Sidharth Praveen