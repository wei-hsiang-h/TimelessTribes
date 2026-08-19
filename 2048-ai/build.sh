#!/usr/bin/env bash

# 1. 安裝 Python 套件
pip install -r requirements.txt

# 2. 如果沒有 nneonneo 的資料夾，就從 GitHub 下載
if [ ! -d "2048-ai" ]; then
  git clone https://github.com/nneonneo/2048-ai.git
fi

# 3. 進入資料夾並編譯 C++ 程式碼 (產出 2048.so)
cd 2048-ai
make
cd ..