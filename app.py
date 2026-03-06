import threading
import os
from flask import Flask, render_template
from flask_socketio import SocketIO, send
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from plyer import notification  # 通知用に追加

app = Flask(__name__)
@app.route('/socket.io.js')
def socket_io_js():
    return app.send_static_file('socket.io.js')
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):
    # 送信されたメッセージを全員に送り返す
    send(msg, broadcast=True)
    
    # --- Windowsのデスクトップ通知を実行 ---
    notification.notify(
        title="社内チャット新着",
        message=msg,
        app_name="MyChat",
        timeout=5 # 通知が表示される秒数
    )

def create_image():
    image = Image.new('RGB', (64, 64), color=(255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.ellipse((10, 10, 54, 54), fill=(0, 120, 215))
    return image

def quit_window(icon, item):
    icon.stop()
    os._exit(0)

# 修正後（クラウド対応版）
def run_flask():
    # クラウド側が割り当てるポート番号を読み取る設定
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)

thread = threading.Thread(target=run_flask, daemon=True)
thread.start()

icon = Icon("mychat_icon", create_image(), "社内チャット実行中", menu=Menu(
    MenuItem("終了", quit_window)
))
icon.run()