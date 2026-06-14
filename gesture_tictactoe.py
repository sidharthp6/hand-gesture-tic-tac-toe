import cv2
import math
import time
import random
import numpy as np
from cvzone.HandTrackingModule import HandDetector

# ───────────────────────────────────────────────────────────────
#  CONFIG
# ───────────────────────────────────────────────────────────────
TARGET_W, TARGET_H = 1280, 720
CELL  = 180
GRID_W = CELL * 3
GRID_H = CELL * 3

# Colors (BGR)
C_BG       = (15, 15, 20)
C_GRID     = (55, 55, 65)
C_X        = (80, 110, 255)    # soft red-orange
C_O        = (80, 220, 130)    # mint green
C_HOVER    = (70, 70, 85)
C_WIN_LINE = (50, 220, 255)    # cyan
C_TEXT     = (210, 210, 215)
C_DIM      = (90, 90, 100)
C_CURSOR   = (0, 255, 160)
C_EASY     = (80, 200, 80)
C_MED      = (80, 180, 255)
C_HARD     = (60, 80, 220)

DIFF_NAMES  = ["Easy", "Medium", "Hard"]
DIFF_COLORS = [C_EASY, C_MED, C_HARD]

CLICK_CD = 0.8    # seconds between moves
RESET_CD = 2.0    # palm hold before reset
DIFF_CD  = 1.5    # between difficulty switches
AI_DELAY = 0.55   # AI "thinking" pause (seconds)

WIN_COMBOS = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6)
]

# ───────────────────────────────────────────────────────────────
#  GAME LOGIC
# ───────────────────────────────────────────────────────────────
def check_winner(board):
    for combo in WIN_COMBOS:
        a, b, c = combo
        if board[a] == board[b] == board[c] != "":
            return board[a], combo
    if "" not in board:
        return "Draw", None
    return None, None

def minimax(board, depth, is_max, alpha, beta, max_depth):
    w, _ = check_winner(board)
    if w == "O":    return 10 - depth
    if w == "X":    return depth - 10
    if w == "Draw": return 0
    if depth >= max_depth: return 0

    if is_max:
        best = -math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = "O"
                best = max(best, minimax(board, depth+1, False, alpha, beta, max_depth))
                board[i] = ""
                alpha = max(alpha, best)
                if beta <= alpha: break
        return best
    else:
        best = math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = "X"
                best = min(best, minimax(board, depth+1, True, alpha, beta, max_depth))
                board[i] = ""
                beta = min(beta, best)
                if beta <= alpha: break
        return best

def ai_best_move(board, diff):
    empty = [i for i in range(9) if board[i] == ""]
    if not empty:
        return None
    if diff == 0:  # Easy — random
        return random.choice(empty)
    max_depth = 3 if diff == 1 else 9  # Medium or Hard
    best_val, move = -math.inf, None
    for i in empty:
        board[i] = "O"
        val = minimax(board, 0, False, -math.inf, math.inf, max_depth)
        board[i] = ""
        if val > best_val:
            best_val, move = val, i
    return move

# ───────────────────────────────────────────────────────────────
#  DRAWING
# ───────────────────────────────────────────────────────────────
def cell_center(idx, OX, OY):
    r, c = divmod(idx, 3)
    return (OX + c*CELL + CELL//2, OY + r*CELL + CELL//2)

def cell_rect(idx, OX, OY):
    r, c = divmod(idx, 3)
    x1, y1 = OX + c*CELL, OY + r*CELL
    return x1, y1, x1+CELL, y1+CELL

def blend_rect(img, x1, y1, x2, y2, color, alpha):
    ov = img.copy()
    cv2.rectangle(ov, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(ov, alpha, img, 1-alpha, 0, img)

def draw_X(img, cx, cy, alpha=1.0):
    half  = int(CELL * 0.30)
    thick = max(4, int(CELL * 0.09))
    ov = img.copy()
    cv2.line(ov, (cx-half, cy-half), (cx+half, cy+half), C_X, thick, cv2.LINE_AA)
    cv2.line(ov, (cx+half, cy-half), (cx-half, cy+half), C_X, thick, cv2.LINE_AA)
    cv2.addWeighted(ov, alpha, img, 1-alpha, 0, img)

def draw_O(img, cx, cy, alpha=1.0):
    r     = int(CELL * 0.30)
    thick = max(4, int(CELL * 0.09))
    ov = img.copy()
    cv2.circle(ov, (cx, cy), r, C_O, thick, cv2.LINE_AA)
    cv2.addWeighted(ov, alpha, img, 1-alpha, 0, img)

def draw_grid(img, OX, OY):
    for i in range(1, 3):
        cv2.line(img, (OX + i*CELL, OY), (OX + i*CELL, OY+GRID_H), C_GRID, 2, cv2.LINE_AA)
        cv2.line(img, (OX, OY + i*CELL), (OX+GRID_W, OY + i*CELL), C_GRID, 2, cv2.LINE_AA)
    cv2.rectangle(img, (OX, OY), (OX+GRID_W, OY+GRID_H), C_GRID, 2)

def draw_hover_cell(img, cell, board, OX, OY):
    if cell is None or board[cell] != "":
        return
    x1, y1, x2, y2 = cell_rect(cell, OX, OY)
    blend_rect(img, x1+2, y1+2, x2-2, y2-2, C_HOVER, 0.40)

def draw_all_pieces(img, board, piece_times, OX, OY):
    now = time.time()
    for i, val in enumerate(board):
        if not val:
            continue
        cx, cy = cell_center(i, OX, OY)
        age   = now - piece_times.get(i, now)
        alpha = min(1.0, age / 0.25)
        if val == "X":
            draw_X(img, cx, cy, alpha)
        else:
            draw_O(img, cx, cy, alpha)

def draw_win_line(img, combo, progress, OX, OY):
    if combo is None:
        return
    s  = cell_center(combo[0], OX, OY)
    e  = cell_center(combo[2], OX, OY)
    ep = (int(s[0] + (e[0]-s[0])*progress), int(s[1] + (e[1]-s[1])*progress))
    cv2.line(img, s, ep, C_WIN_LINE, 5, cv2.LINE_AA)

def put(img, text, x, y, font=cv2.FONT_HERSHEY_SIMPLEX, scale=0.65, color=None, thick=1):
    cv2.putText(img, text, (x, y), font, scale, color or C_TEXT, thick, cv2.LINE_AA)

def draw_score_panel(img, score, OY):
    x, y = 30, OY + 20
    put(img, "SCORE", x, y, scale=0.6, color=C_DIM)
    y += 45
    for label, key, color in [("You  (X)", "X", C_X), ("AI   (O)", "O", C_O), ("Draw", "D", C_DIM)]:
        put(img, label, x, y, scale=0.55, color=color)
        y += 28
        put(img, str(score[key]), x+8, y, cv2.FONT_HERSHEY_DUPLEX, 1.3, color, 2)
        y += 52

def draw_right_panel(img, diff, ai_thinking, OX, OY):
    x = OX + GRID_W + 30
    y = OY + 20

    put(img, "DIFFICULTY", x, y, scale=0.6, color=C_DIM)
    y += 38
    put(img, DIFF_NAMES[diff], x, y, cv2.FONT_HERSHEY_DUPLEX, 1.1, DIFF_COLORS[diff], 2)
    y += 55

    if ai_thinking:
        dots = "." * (int(time.time() * 3) % 4)
        put(img, "AI thinking" + dots, x, y, scale=0.6, color=C_O)
    y += 40

    put(img, "GESTURES", x, y, scale=0.6, color=C_DIM)
    y += 32
    for g, a in [("Index finger", "Place X"), ("Peace sign", "Cycle difficulty"), ("Open palm", "Reset game")]:
        put(img, g, x, y, scale=0.52, color=C_TEXT)
        y += 22
        put(img, "  -> " + a, x, y, scale=0.48, color=C_DIM)
        y += 30

def draw_title(img, WIDTH):
    title = "Hand Gesture Tic Tac Toe"
    (tw, _), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_DUPLEX, 1.0, 2)
    put(img, title, (WIDTH-tw)//2, 44, cv2.FONT_HERSHEY_DUPLEX, 1.0, C_TEXT, 2)
    sub = "by Sidharth Praveen"
    (sw, _), _ = cv2.getTextSize(sub, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)
    put(img, sub, (WIDTH-sw)//2, 66, scale=0.52, color=C_DIM)

def draw_result_banner(img, winner, OX, OY):
    if not winner:
        return
    if winner == "Draw":
        txt, color = "It's a Draw!", C_DIM
    elif winner == "X":
        txt, color = "You Win!  :)", C_X
    else:
        txt, color = "AI Wins!", C_O

    blend_rect(img, OX, OY+GRID_H+8, OX+GRID_W, OY+GRID_H+80, (20, 20, 25), 0.85)
    (tw, _), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_DUPLEX, 1.2, 2)
    put(img, txt, OX+(GRID_W-tw)//2, OY+GRID_H+55, cv2.FONT_HERSHEY_DUPLEX, 1.2, color, 2)
    hint = "Show open palm to play again"
    (hw, _), _ = cv2.getTextSize(hint, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)
    put(img, hint, OX+(GRID_W-hw)//2, OY+GRID_H+95, scale=0.52, color=C_DIM)

def draw_cursor(img, x, y):
    cv2.circle(img, (x, y), 11, C_CURSOR, -1, cv2.LINE_AA)
    cv2.circle(img, (x, y), 13, (255, 255, 255), 1, cv2.LINE_AA)

# ───────────────────────────────────────────────────────────────
#  MAIN
# ───────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)
cap.set(3, TARGET_W)
cap.set(4, TARGET_H)

WIDTH  = int(cap.get(3))
HEIGHT = int(cap.get(4))
OX = (WIDTH  - GRID_W) // 2
OY = (HEIGHT - GRID_H) // 2

bg = np.full((HEIGHT, WIDTH, 3), C_BG, dtype=np.uint8)  # dark background (created once)

detector = HandDetector(detectionCon=0.8, maxHands=1)

board          = [""] * 9
piece_times    = {}
score          = {"X": 0, "O": 0, "D": 0}
difficulty     = 2        # 0=Easy  1=Medium  2=Hard
winner         = None
win_combo      = None
win_anim_start = None
ai_move_time   = None
last_click     = 0
last_reset     = 0
last_diff      = 0

while True:
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    hands, frame = detector.findHands(frame, draw=False)

    now = time.time()

    # ── Scheduled AI move ──────────────────────────────────────
    if ai_move_time and now >= ai_move_time:
        ai = ai_best_move(board, difficulty)
        if ai is not None:
            board[ai] = "O"
            piece_times[ai] = now
            winner, win_combo = check_winner(board)
            if winner:
                if winner == "O":      score["O"] += 1
                elif winner == "Draw": score["D"] += 1
                win_anim_start = now
        ai_move_time = None

    # ── Win line animation progress ─────────────────────────────
    win_progress = 1.0
    if win_anim_start:
        win_progress = min(1.0, (now - win_anim_start) / 0.5)

    # ── Gesture handling ────────────────────────────────────────
    hovered    = None
    cursor_pos = None

    if hands:
        hand    = hands[0]
        fingers = detector.fingersUp(hand)
        tip     = hand["lmList"][8]
        cx, cy  = tip[0], tip[1]
        cursor_pos = (cx, cy)

        # Open palm -> reset
        if fingers == [1,1,1,1,1] and now - last_reset > RESET_CD:
            board          = [""] * 9
            piece_times    = {}
            winner         = None
            win_combo      = None
            win_anim_start = None
            ai_move_time   = None
            last_reset     = now
            last_click     = now  # avoid instant move after reset

        # Peace sign -> cycle difficulty
        elif fingers == [0,1,1,0,0] and now - last_diff > DIFF_CD:
            difficulty = (difficulty + 1) % 3
            last_diff  = now

        # Index finger -> hover / place
        elif fingers == [0,1,0,0,0] and winner is None and ai_move_time is None:
            gx = (cx - OX) // CELL
            gy = (cy - OY) // CELL
            if 0 <= gx < 3 and 0 <= gy < 3:
                cell    = int(gy*3 + gx)
                hovered = cell
                if now - last_click > CLICK_CD and board[cell] == "":
                    board[cell]       = "X"
                    piece_times[cell] = now
                    last_click        = now
                    winner, win_combo = check_winner(board)
                    if winner:
                        if winner == "X":      score["X"] += 1
                        elif winner == "Draw": score["D"] += 1
                        win_anim_start = now
                    else:
                        ai_move_time = now + AI_DELAY

    # ── Compose frame ────────────────────────────────────────────
    cv2.addWeighted(bg, 0.82, frame, 0.18, 0, frame)
    img = frame

    draw_hover_cell(img, hovered, board, OX, OY)
    draw_grid(img, OX, OY)
    draw_all_pieces(img, board, piece_times, OX, OY)
    if win_combo:
        draw_win_line(img, win_combo, win_progress, OX, OY)
    draw_score_panel(img, score, OY)
    draw_right_panel(img, difficulty, ai_move_time is not None, OX, OY)
    draw_title(img, WIDTH)
    draw_result_banner(img, winner, OX, OY)
    if cursor_pos:
        draw_cursor(img, *cursor_pos)

    cv2.imshow("Hand Gesture Tic Tac Toe  -  Sidharth Praveen", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
