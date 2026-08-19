#!/usr/bin/env bash

# 1. 安裝 Python 套件
pip install -r requirements.txt

# 2. 如果沒有 ai_core 資料夾，就從 GitHub 下載並重新命名
if [ ! -d "ai_core" ]; then
  git clone https://github.com/nneonneo/2048-ai.git ai_core
fi

# 3. 進入資料夾並編譯 C++ 程式碼 (產出 2048.so)
cd ai_core
g++ -O3 -shared -fPIC 2048.cpp -o 2048.so
cd ..
