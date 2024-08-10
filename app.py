from flask import Flask, render_template, request, send_from_directory, redirect, session, make_response
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from os import path
from secrets import token_hex
from datetime import datetime
from random import randint

import dbHandler
from MyJWT import JWT

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vn^F8t*#klq3P0(mE6W{9!`l>GU5N$e8'
socketioApp  = SocketIO(app)
myjwt = JWT()
myjwt.set_secret_key('N*YV$%NY*#4vJWKRQOcnqvb3v$N37]85n&#583?vNT583#`Yv83')


chatrooms = {}


def getRoomCode():
  while True:
    code = token_hex(3)
    if not code in chatrooms.keys():
      return code


def createMessage(sender='', message=''):
  return {'sender': sender, 'message': message, 'time': datetime.now().strftime('%-d. %-m. %Y %H:%M')}


def checkCaptcha(captchaNum: int, captchaInp: str):
  with open('static/captcha/captcha.txt', 'r') as f:
    content = f.read().split('\n')
  return content[captchaNum-1] == captchaInp


@socketioApp.on("connect")
def io_connect(_):
  name = session.get('name')
  code = session.get('room')
  if name is None or code is None:
    return
  if not code in chatrooms:
    leave_room(code)
  join_room(code)
  msg = createMessage('', f"{name} has joined the room!")
  send(msg, to=code)
  emit("Dis/Connect", {'change': "+"}, to=code)
  chatrooms[code]['members'] += 1
  chatrooms[code]['messages'].append(msg)


@socketioApp.on("message")
def io_message(message):
  name = session.get('name')
  code = session.get('room')
  if name is None or code is None or not code in chatrooms:
    return
  msg = createMessage(name, message['message'])
  send(msg, to=code)
  chatrooms[code]['messages'].append(msg)


@socketioApp.on("disconnect")
def io_disconnect():
  name = session.get('name')
  code = session.get('room')
  leave_room(code)
  if code in chatrooms:
    chatrooms[code]['members'] -= 1
    msg = createMessage('', f"{name} has left the room!")
    send(msg, to=code)
    emit("Dis/Connect", {'change': "-"}, to=code)
    chatrooms[code]['messages'].append(msg)
    if chatrooms[code]['members'] <= 0:
      del chatrooms[code]


# Used on sign page to check for username
@socketioApp.on("usernameInUse")
def io_checkUsernameInUse(data):
  rep = 'Y' if dbHandler.checkIfUsernameExists(data['username']) else 'N'
  emit("usernameInUseReply", {'status': rep})


@app.route('/sign')
def signuporin():
  e = request.args.get('e')
  return render_template('registerlogin.html', captcha=randint(1, 10), error=e if e else '')


@app.route('/register', methods=['POST'])
def register():
  username = request.form.get('name')
  password = request.form.get('password')
  check = request.form.get('check')
  captcha = request.form.get('captcha')
  captchainp = request.form.get('captchainp')
  if dbHandler.checkIfUsernameExists(username): return redirect('/sign?e=Username already in use')
  if len(password) < 8: return redirect('/sign?e=Password must be at least 8 characters')
  if check != password: return redirect('/sign?e=Passwords don\'t match')
  if not checkCaptcha(int(captcha), captchainp): return redirect('/sign?e=Invalid captcha')
  # Now we can register the user
  dbHandler.addUser(username, password)
  return redirect('/sign?e=Great! Now log in')


@app.route('/login', methods=['POST'])
def login():
  username = request.form.get('name')
  password = request.form.get('password')
  uix = dbHandler.logInUser(username, password)
  if uix == -1: return redirect('/sign?e=Incorrect username or password')
  resp = make_response(redirect('/'))
  data = {'uix': uix}
  JWT_token, JWT_user_context = myjwt.jwtencode(data)
  resp.set_cookie('JWT_token', JWT_token)
  resp.set_cookie('JWT_user_context', JWT_user_context, httponly=True, samesite='Strict')
  return resp


@app.route('/chat')
def chat():
  name = session.get('name')
  code = session.get('room')
  if not name or not code or not code in chatrooms:
    return redirect('/')
  return render_template('chat.html', name=name, room=code, messages=chatrooms[code]['messages'], personCount=chatrooms[code]['members']) # possibly add 1


@app.route('/favicon.ico')
def favicon():
  return send_from_directory(path.join(app.root_path, 'static/icon'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'GET':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    if JWT_token is None or JWT_user_context is None:
      return redirect('/sign')
    i, data = myjwt.jwtdecode(JWT_token, JWT_user_context)
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
  dbHandler.initialize()
  socketioApp.run(app, port=5000, host='0.0.0.0')


if __name__ == '__main__':
  main()
