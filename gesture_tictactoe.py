import cv2, math, time
import numpy as np
from cvzone.HandTrackingModule import HandDetector

# ---------- GAME LOGIC ----------
def check_winner(board):
    combos = [(0,1,2),(3,4,5),(6,7,8),
              (0,3,6),(1,4,7),(2,5,8),
              (0,4,8),(2,4,6)]
    for a,b,c in combos:
        if board[a]==board[b]==board[c] and board[a]!="":
            return board[a]
    if "" not in board:
        return "Draw"
    return None

def minimax(board, depth, is_max, alpha, beta):
    winner = check_winner(board)
    if winner=="O": return 1
    if winner=="X": return -1
    if winner=="Draw": return 0
    if is_max:
        best=-math.inf
        for i in range(9):
            if board[i]=="":
                board[i]="O"
                val=minimax(board,depth+1,False,alpha,beta)
                board[i]=""
                best=max(best,val)
                alpha=max(alpha,val)
                if beta<=alpha: break
        return best
    else:
        best=math.inf
        for i in range(9):
            if board[i]=="":
                board[i]="X"
                val=minimax(board,depth+1,True,alpha,beta)
                board[i]=""
                best=min(best,val)
                beta=min(beta,val)
                if beta<=alpha: break
        return best

def best_move(board):
    best_val = -math.inf
    move = None
    for i in range(9):
        if board[i] == "":
            board[i] = "O"
            val = minimax(board, 0, False, -math.inf, math.inf)
            board[i] = ""
            if val > best_val:
                best_val = val
                move = i
    return move

# ---------- CAMERA + HAND SETUP ----------
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
detector = HandDetector(detectionCon=0.8, maxHands=1)

board = [""]*9
cell_size = 120
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
grid_width = cell_size * 3
grid_height = cell_size * 3
offset_x = (frame_width - grid_width) // 2
offset_y = (frame_height - grid_height) // 2
last_click = 0
last_reset = 0

def draw_board(img, board):
    for i in range(3):
        for j in range(3):
            x1 = offset_x + j*cell_size
            y1 = offset_y + i*cell_size
            x2, y2 = x1+cell_size, y1+cell_size
            cv2.rectangle(img,(x1,y1),(x2,y2),(255,255,255),2)
            val = board[i*3+j]
            if val!="":
                cv2.putText(img,val,(x1+35,y1+90),
                            cv2.FONT_HERSHEY_SIMPLEX,2.5,(0,255,255),3)

# ---------- MAIN LOOP ----------
while True:
    success, img = cap.read()
    if not success:
        break
    img = cv2.flip(img,1)
    hands, img = detector.findHands(img, draw=False)

    winner = check_winner(board)

    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        index_tip = hand["lmList"][8]
        x, y = index_tip[0], index_tip[1]
        cv2.circle(img,(x,y),10,(0,255,0),-1)

        # --- Gesture-based reset (open palm ✋) ---
        if fingers == [1,1,1,1,1] and time.time()-last_reset>2:
            board = [""]*9
            last_reset = time.time()
            last_click = 0
            cv2.putText(img,"↻ Reset!",(offset_x,offset_y+grid_height+40),
                        cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,255,0),3)
            cv2.imshow("Hand Gesture Tic Tac Toe - Sidharth Praveen", img)
            cv2.waitKey(400)
            continue

        # --- Play move (index finger ☝️) ---
        if fingers == [0,1,0,0,0] and winner is None:
            grid_x = (x - offset_x)//cell_size
            grid_y = (y - offset_y)//cell_size
            if 0 <= grid_x < 3 and 0 <= grid_y < 3:
                cell = int(grid_y*3 + grid_x)
                if time.time()-last_click > 0.8:
                    if board[cell] == "":
                        board[cell] = "X"
                        last_click = time.time()
                        winner = check_winner(board)
                        if not winner:
                            ai = best_move(board)
                            if ai is not None:
                                board[ai] = "O"

    # ---------- Draw everything ----------
    draw_board(img, board)
    winner = check_winner(board)
    if winner:
        text = "Draw" if winner=="Draw" else (winner+" Wins!")
        cv2.putText(img,text,(offset_x,offset_y+grid_height+40),
                    cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,255,255),3)
        cv2.putText(img,"Show Open Palm ✋ to Restart",
                    (offset_x,offset_y+grid_height+80),
                    cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255),2)

    # ---------- Title and signature ----------
    title_text = "Tic Tac Toe AI"
    font = cv2.FONT_HERSHEY_DUPLEX
    (title_w, title_h), _ = cv2.getTextSize(title_text, font, 1.4, 3)
    title_x = (frame_width - title_w) // 2
    title_y = 40
    cv2.putText(img, title_text, (title_x, title_y), font, 1.4, (255,255,255), 3)

    name_text = "by Sidharth"
    (name_w, _), _ = cv2.getTextSize(name_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    name_x = (frame_width - name_w) // 2
    name_y = title_y + 30
    cv2.putText(img, name_text, (name_x, name_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180,180,180), 2)

    cv2.imshow("Hand Gesture Tic Tac Toe - Sidharth Praveen", img)
    key = cv2.waitKey(1) & 0xFF
    if key==27:
        break

cap.release()
cv2.destroyAllWindows()
