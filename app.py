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


@socketioApp.on("connect")
def io_connect():
  name = session.get('name')
  code = session.get('room')
  if name is None or code is None:
    return
  if not code in chatrooms:
    leave_room(code)
  join_room(code)
  send(f"{name} has joined the room!", to=code)
  chatrooms[code]['members'] += 1
  chatrooms[code]['messages'].append(f"{name} has joined the room!")


@socketioApp.on("message")
def io_message(msg):
  name = session.get('name')
  code = session.get('room')
  if name is None or code is None or not code in chatrooms:
    return
  message = f'{name}: {msg["message"]}'
  send(message, to=code)
  chatrooms[code]['messages'].append(message)


@socketioApp.on("disconnect")
def io_disconnect():
  name = session.get('name')
  code = session.get('room')
  leave_room(code)
  if code in chatrooms:
    chatrooms[code]['members'] -= 1
    if chatrooms[code]['members'] <= 0:
      del chatrooms[code]
    send(f'{name} has left the chat!', to=code)


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
