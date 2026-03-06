import os
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 修正：DATABASE_URLの読み込みと変換を確実に行う
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 以下、Messageクラスなどの続きはそのまま

app = Flask(__name__)
# データベースとの接続設定
uri = os.environ.get("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# データベースのテーブル（保存形式）の定義
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)

socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    # ページを開いた時に過去のメッセージをすべて読み出す
    messages = Message.query.all()
    return render_template('index.html', messages=messages)

@socketio.on('message')
def handle_message(msg):
    # メッセージをデータベースに保存
    new_message = Message(content=msg)
    db.session.add(new_message)
    db.session.commit()
    send(msg, broadcast=True)

@socketio.on('clear_history')
# 既存の handle_clear 関数の下あたりから書き換え
if __name__ == "__main__":
    with app.app_context():
        # ここで「保存箱（テーブル）」を強制的に作成します
        db.create_all()
        print("Database tables created!") 

    port = int(os.environ.get("PORT", 5000))
    # eventletを使用してサーバーを起動
    socketio.run(app, host='0.0.0.0', port=port)
