import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, render_template
# ...（以下は今のコードのままでOKです）


import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# データベース設定
uri = os.environ.get("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# データベースの保存形式
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg_content = request.form.get('content')
        if msg_content:
            new_message = Message(content=msg_content)
            db.session.add(new_message)
            db.session.commit()
        return redirect(url_for('index'))
    
    messages = Message.query.all()
    return render_template('index.html', messages=messages)

@app.route('/clear', methods=['POST'])
def clear():
    Message.query.delete()
    db.session.commit()
    return redirect(url_for('index'))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

