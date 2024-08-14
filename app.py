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


def createMessage(sender='', message=''):
  return {'sender': sender, 'message': message, 'time': datetime.now().strftime('%d. %m. %Y %H:%M')}


def checkCaptcha(captchaNum: int, captchaInp: str):
  with open('static/captcha/captcha.txt', 'r') as f:
    content = f.read().split('\n')
  return content[captchaNum-1] == captchaInp


@socketioApp.on("connect")
def io_connect(_):
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isAuthentic, data = myjwt.jwtdecode(JWT_token, JWT_user_context)
  if not isAuthentic: return
  code = session.get('code')
  if not code:
    return
  if not dbHandler.checkIfCodeExists(code):
    leave_room(code)
  join_room(code)
  #emit("Dis/Connect", {'change': "+"}, to=code)


@socketioApp.on("message")
def io_message(message):
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isAuthentic, data = myjwt.jwtdecode(JWT_token, JWT_user_context)
  if not isAuthentic: return
  code = session.get('code')
  if not code or not dbHandler.checkIfCodeExists(code):
    return
  msg = createMessage(dbHandler.getUsername(data['uix']), message['message'])
  send(msg, to=code)
  dbHandler.addMessage(code, msg)


@socketioApp.on("disconnect")
def io_disconnect():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isAuthentic, data = myjwt.jwtdecode(JWT_token, JWT_user_context)
  if not isAuthentic: return
  code = session.get('code')
  if not code:
    return
  leave_room(code)


# Used on sign page to check for username
@socketioApp.on("usernameInUse")
def io_checkUsernameInUse(data):
  rep = 'Y' if dbHandler.checkIfUsernameExists(data['username']) else 'N'
  emit("usernameInUseReply", {'status': rep})


# Used on index page to check for code in server creation
@socketioApp.on("codeInUse")
def io_checkCodeInUse(data):
  rep = 'Y' if dbHandler.checkIfCodeExists(data['code']) else 'N'
  emit("codeInUseReply", {'status': rep})


@app.route('/sign')
def flask_signuporin():
  if session.get('code'): session['code'] = ''
  e = request.args.get('e')
  return render_template('registerlogin.html', captcha=randint(1, 10), error=e if e else '')


@app.route('/register', methods=['POST'])
def flask_register():
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
def flask_login():
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


@app.route('/create', methods=['POST'])
def flask_createServer():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isAuthentic, data = myjwt.jwtdecode(JWT_token, JWT_user_context)
  if not isAuthentic: return redirect('/sign')
  serverName = request.form.get('name')
  serverCode = request.form.get('code')
  if not serverName or not serverCode: return redirect('/')
  dbHandler.addServer(serverName, serverCode, data['uix'])
  return redirect('/')


@app.route('/logout', methods=['POST'])
def flask_logout():
  resp = make_response(redirect('/sign'))
  resp.set_cookie('JWT_token', '', expires=0)
  resp.set_cookie('JWT_user_context', '', expires=0)
  return resp


@app.route('/delete', methods=['POST'])
def flask_deleteAccount():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isAuthentic, data = myjwt.jwtdecode(JWT_token, JWT_user_context)
  if not isAuthentic: return redirect('/sign')
  dbHandler.removeUser(data['uix'])
  resp = make_response(redirect('/sign'))
  resp.set_cookie('JWT_token', '', expires=0)
  resp.set_cookie('JWT_user_context', '', expires=0)
  return resp


@app.route('/join', methods=['POST'])
def flask_joinServer():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isAuthentic, data = myjwt.jwtdecode(JWT_token, JWT_user_context)
  if not isAuthentic: return redirect('/sign')
  serverCode = request.form.get('code')
  if not serverCode: return redirect('/')
  dbHandler.userJoinServer(data['uix'], serverCode)
  return redirect('/')


@app.route('/chat/<code>')
def flask_chat(code):
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isAuthentic, data = myjwt.jwtdecode(JWT_token, JWT_user_context)
  if not isAuthentic: return redirect('/sign')
  username = dbHandler.getUsername(data['uix'])
  serverInfo = dbHandler.getServerInfo(code)
  if not dbHandler.isUserInServer(data['uix'], serverInfo[0]): return redirect('/')
  session['code'] = code
  return render_template('chat.html', name=username, room=code, messages=dbHandler.getMessages(code), personCount=0) ################## PERSON COUNT FINISH


@app.route('/favicon.ico')
def flask_favicon():
  return send_from_directory(path.join(app.root_path, 'static/icon'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET'])
def flask_index():
  if session.get('code'): session['code'] = ''
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isAuthentic, data = myjwt.jwtdecode(JWT_token, JWT_user_context)
  if not isAuthentic: return redirect('/sign')
  userServers = dbHandler.getUserServers(data['uix'])
  return render_template('index.html', serverList=userServers, serverCount=len(userServers))


def main():
  dbHandler.initialize()
  socketioApp.run(app, port=5000, host='0.0.0.0')


if __name__ == '__main__':
  main()
