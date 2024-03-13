from flask import Flask, render_template, request, send_from_directory, redirect, session
from flask_socketio import SocketIO, join_room, leave_room, send
from os import path
from secrets import token_hex


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vn^F8t*#klq3P0(mE6W{9!`l>GU5N$e8'
socketioApp  = SocketIO(app)


chatrooms = {}


def getRoomCode():
  while True:
    code = token_hex(3)
    if not code in chatrooms.keys():
      return code


@app.route('/chat')
def chat():
  name = session.get('name')
  code = session.get('room')
  if not name or not code or not code in chatrooms:
    return redirect('/')
  return render_template('chat.html', name=name, room=code, messages=chatrooms[code]['messages'])


@app.route('/favicon.ico')
def favicon():
  return send_from_directory(path.join(app.root_path, 'static/icon'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET', 'POST'])
def index():
  session.clear()
  if request.method == 'GET':
    return render_template('index.html')
  else:
    name = request.form.get('name')
    join = True if request.form.get('join') == 'yes' else False
    code = request.form.get('code')
    if not name:
      return render_template('index.html', error='Please enter a name!')
    if join:
      if not code:
        return render_template('index.html', error='Please enter a code!')
      if not code in chatrooms:
        return render_template('index.html', error='Invalid code!')
      roomCode = code
    else:
      roomCode = getRoomCode()
      chatrooms[roomCode] = {'members': 0, 'messages': []}
    session['name'] = name
    session['room'] = roomCode
    return redirect('/chat')


def main():
  socketioApp.run(app, port=80)


if __name__ == '__main__':
  main()
