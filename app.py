import os
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# データベースURLの読み込みと変換（Renderの仕様に合わせる）
uri = os.environ.get("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# データベースの保存形式（テーブル）の定義
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)

socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    # ページを開いた時に過去のメッセージをすべて表示
    messages = Message.query.all()
    return render_template('index.html', messages=messages)

@socketio.on('message')
def handle_message(msg):
    # メッセージを保存する
    new_message = Message(content=msg)
    db.session.add(new_message)
    db.session.commit()
    send(msg, broadcast=True)

@socketio.on('clear_history')
def handle_clear():
    # 履歴をすべて削除する
    Message.query.delete()
    db.session.commit()
    emit('history_cleared', broadcast=True)

if __name__ == "__main__":
    with app.app_context():
        # 初回起動時に保存用の「箱」を作成する
        db.create_all()
    
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
