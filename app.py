# app.py や w_app.py の socketイベント部分
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
import random
import uuid
import csv

app = Flask(__name__)
socketio = SocketIO(app)

# 単語ペア読み込み
import pandas as pd
import os

def load_word_pairs():
    csv_path = os.path.join(os.path.dirname(__file__), 'word_pairs.csv')
    df = pd.read_csv(csv_path, header=None)  # ヘッダーなしで読み込み
    pairs = list(zip(df[0].str.strip(), df[1].str.strip()))
    return pairs


word_pairs = load_word_pairs()

# 各ルームごとにデータを保持
rooms = {}

@app.route("/")
def index():
    room_id = str(uuid.uuid4())[:8]
    return redirect(url_for("room", room_id=room_id))

@app.route("/room/<room_id>")
def room(room_id):
    return render_template("room.html", room_id=room_id)

@socketio.on("join")
def handle_join(data):
    room = data["room"]
    user_type = data["type"]  # "kazu" or "rino"

    # 毎回ランダムペアを選び直す（再読み込みでも更新されるように）
    pair = random.choice(word_pairs)

    if room not in rooms:
        rooms[room] = {}

    # 現在の参加者の情報を更新
    rooms[room][user_type] = request.sid
    rooms[room]["pair"] = pair  # 毎回新しいペアに更新

    # 自分の単語を送信
    word = pair[0] if user_type == "kazu" else pair[1]
    emit("word", {"word": word}, room=request.sid)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
