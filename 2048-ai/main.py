import ctypes
import math
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

# 允許跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 載入 nneonneo 編譯好的 C++ 函式庫
lib_path = os.path.join(os.path.dirname(__file__), '2048-ai', '2048.so')
if os.path.exists(lib_path):
    lib = ctypes.CDLL(lib_path)
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
    
    board_int64 = board_to_int64(state.board)
    move_code = lib.find_best_move(board_int64)
    
    move_map = {0: "UP (上)", 1: "DOWN (下)", 2: "LEFT (左)", 3: "RIGHT (右)"}
    best_move = move_map.get(move_code, "UNKNOWN")
    
    return {"best_move": best_move}

# 將 static 資料夾掛載為前端網頁
app.mount("/", StaticFiles(directory="static", html=True), name="static")