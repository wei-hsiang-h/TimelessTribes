import ctypes
import math
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

lib_path = os.path.join(os.path.dirname(__file__), 'ai_core', '2048.so')
if os.path.exists(lib_path):
    lib = ctypes.CDLL(lib_path)
    lib.init_tables()
    lib.find_best_move.argtypes = [ctypes.c_uint64]
    lib.find_best_move.restype = ctypes.c_int
else:
    lib = None
    print("警告：找不到 2048.so，請確認是否有執行 build.sh")

class BoardState(BaseModel):
    board: list[list[int]]

def board_to_int64(board_array):
    board_int = 0
    for i in range(16):
        row = i // 4
        col = i % 4
        val = board_array[row][col]
        if val > 0:
            power = int(math.log2(val))
            board_int |= (power << (4 * i))
    return board_int

@app.post("/api/get_best_move")
def get_best_move(state: BoardState):
    if not lib:
        return {"error": "AI 核心尚未載入"}
    
    # === 自訂規則：防止 2048 互相合成 ===
    seen_2048_count = 0
    for r in range(4):
        for c in range(4):
            if state.board[r][c] == 2048:
                if seen_2048_count > 0:
                    # 將多餘的 2048 提升為 4096, 8192... 變為不可跨越的障礙物
                    state.board[r][c] = 2048 * (2 ** seen_2048_count)
                seen_2048_count += 1
    
    board_int64 = board_to_int64(state.board)
    move_code = lib.find_best_move(board_int64)
    
    move_map = {0: "UP (上)", 1: "DOWN (下)", 2: "LEFT (左)", 3: "RIGHT (右)"}
    best_move = move_map.get(move_code, "UNKNOWN")
    
    return {"best_move": best_move}

# 將 static 資料夾掛載為前端網頁
app.mount("/", StaticFiles(directory="static", html=True), name="static")
