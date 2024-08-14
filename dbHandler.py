import sqlite3
from hashlib import sha256
from secrets import token_hex

from logs import Logger
logger = Logger()

DBLOCATION = 'data/database.db'

# Initialize all database tables
def initialize() -> True:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    # Table for users
    cursor.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, salt TEXT NOT NULL, password TEXT NOT NULL, privilegeLevel INT NOT NULL);')
    cursor.execute('CREATE TABLE IF NOT EXISTS userServerMember(id INTEGER PRIMARY KEY AUTOINCREMENT, userId INTEGER NOT NULL, serverId INTEGER NOT NULL, CONSTRAINT FK_userId FOREIGN KEY(userId) REFERENCES users(id), CONSTRAINT FK_serverId FOREIGN KEY(serverId) REFERENCES servers(id));')
    cursor.execute('CREATE TABLE IF NOT EXISTS servers(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, code TEXT NOT NULL UNIQUE, owner INT NOT NULL, CONSTRAINT FK_owner FOREIGN KEY(owner) REFERENCES users(id));')
    cursor.execute('CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT NOT NULL, sender TEXT NOT NULL, time TEXT NOT NULL, serverId INTEGER NOT NULL, CONSTRAINT FK_serverId FOREIGN KEY(serverId) REFERENCES servers(id));')
  except sqlite3.Error as e:
    logger.log('An error in SQL syntax occurred while initializing tables')
  except Exception as e:
    logger.log(f'An unexpected error occurred while initializing tables; Error message: {e}')
  db.commit()
  return True


# Hash a password, returns salt,hash tuple
def hashPassword(password: str) -> tuple[str, str]:
  try:
    # Random salt
    salt = token_hex(32)
    # Hashed password with salt
    hashed = sha256(bytes.fromhex(salt) + bytes(password, 'utf-8')).hexdigest()
    return salt, hashed
  except Exception as e:
    logger.log(f'An unexpected error occurred while hashing a password; Error message: {e}')
  return '', ''


# Check provided password, salt with a hash, returns bool
def checkHashedPassword(password: str, salt: str, checkHash: str) -> bool:
  try:
    return sha256(bytes.fromhex(salt) + bytes(password, 'utf-8')).hexdigest() == checkHash
  except Exception as e:
    logger.log(f'An unexpected error occurred while checking a hashed password; Error message: {e}')
  return False



# Log in a user; returns id (if fail -> id = -1)
def logInUser(username: str, password: str) -> int:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    # Get id, salt and password of a username
    account = cursor.execute('SELECT id, salt, password FROM users WHERE username = ?;', (username,))
    account = account.fetchone()
    # Check if the username exists
    if account:
      # Check if the password is right
      if (checkHashedPassword(password, account[1], account[2])):
        return account[0]
      else:
        logger.log(f'Password didn\'t match for user {username}', 2)
    else:
      logger.log(f'Unknown username: {username}', 2)
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while logging in a user; Error message: {e}; Data: {(username, password)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while logging in a user; Error message: {e}')
  db.commit()
  return -1


# Get a privLevel associated with userId, returns privLevel (or -1 if fail)
def getUserPrivilege(ix: int) -> int:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    res1 = cursor.execute('SELECT privilegeLevel FROM users WHERE id = ?;', (ix,))
    res1 = res1.fetchone()
    db.commit()
    if res1:
      return res1[0]
    logger.log(f'Couldn\'t find row while checking for a privilege level; Error message: {e}; Data: {(ix)}', 2)
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while checking for a privilege level; Error message: {e}; Data: {(ix)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while checking for a privilege level; Error message: {e}')
  db.commit()
  return -1


# Get a privLevel associated with userId, returns privLevel (or -1 if fail)
def getUsername(ix: int) -> str:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    res1 = cursor.execute('SELECT username FROM users WHERE id = ?;', (ix,))
    res1 = res1.fetchone()
    db.commit()
    if res1:
      return res1[0]
    logger.log(f'Couldn\'t find row while checking for a privilege level; Error message: {e}; Data: {(ix)}', 2)
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while checking for a privilege level; Error message: {e}; Data: {(ix)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while checking for a privilege level; Error message: {e}')
  db.commit()
  return -1


# Return True if Username was found in table
def checkIfUsernameExists(username: str) -> bool:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    # If username is in users
    res1 = cursor.execute('SELECT * FROM users WHERE username = ?;', (username,))
    res1 = res1.fetchall()
    db.commit()
    if res1:
      print(res1)
      return True
    return False
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while checking if a username already exists; Error message: {e}; Data: {(username)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while checking if a username already exists; Error message: {e}')
  db.commit()
  return True


def addUser(username: str, password: str, privilegeLevel=0) -> True:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    # Hash the password
    salt, hashed = hashPassword(password)
    # Data for INSERT
    data = (username, salt, hashed, privilegeLevel)
    # INSERT into users table
    cursor.execute('INSERT INTO users(username, salt, password, privilegeLevel) VALUES(?, ?, ?, ?);', data)
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while adding a user {privilegeLevel}; Error message: {e}; Data: {(username, salt, password)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while adding a user {privilegeLevel}; Error message: {e}')
  db.commit()
  return True


# Change targets privilege level
def changePrivLevel(ix :int, privLevel: int) -> True:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    # Change the privilegeLevel
    cursor.execute('UPDATE users SET privilegeLevel=? WHERE id = ?;', (privLevel, ix))
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while changing privilege level; Error message: {e}; Data: {(ix)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while changing privilege level; Error message: {e}')
  db.commit()
  return True


# Remove a user
def removeUser(ix: int) -> True:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    # Find a user
    user = cursor.execute('SELECT username FROM users WHERE id = ?;', (ix,))
    user = user.fetchone()
    if user:
      # First remove user's servers
      res = cursor.execute('SELECT code FROM servers WHERE owner = ?', (ix,))
      res = res.fetchall()
      for server in res: removeServer(server[0])
      # Second remove userServer rels.
      cursor.execute('DELETE FROM userServerMember WHERE userId = ?', (ix,))
      # Then remove user
      cursor.execute('DELETE FROM users WHERE id = ?', (ix,))
    else:
      # If we were unable to find the id in users, we log it as a warning
      logger.log(f'Recieved remove request for id({ix}), however requested row is not present in users table aborting', 2)
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while removing a user; Error message: {e}; Data: {(ix)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while removing a user; Error message: {e}')
  db.commit()
  return True




def addServer(name: str, roomcode: str, ownerix: int) -> bool:
  try:
    if (checkIfCodeExists(roomcode)):
      logger.log(f'Roomcode {roomcode} already exists!', 2)
      return False
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    # Table for users
    cursor.execute('INSERT INTO servers(name, code, owner) VALUES(?, ?, ?);', (name, roomcode, ownerix))
    db.commit()
    userJoinServer(ownerix, roomcode)
    return True
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while adding server; Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while adding server; Error message: {e}')
  db.commit()
  return False


def checkIfCodeExists(roomcode: str) -> bool:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    # Table for users
    res = cursor.execute('SELECT * FROM servers WHERE code = ?', (roomcode,))
    res = res.fetchall()
    db.commit()
    if res:
      return True
    return False
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while checking if code exists; Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while checking if code exists; Error message: {e}')
  db.commit()
  return True


def removeServer(roomcode: str) -> True:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    six = getServerId(roomcode)
    if six != -1:
      # 1st remove all messages
      cursor.execute('DELETE FROM messages WHERE serverId = ?', (six,))
      # Then remove all user-server rels.
      cursor.execute('DELETE FROM userServerMember WHERE serverId = ?', (six,))
      # Finally remove server
      cursor.execute('DELETE FROM servers WHERE id = ?', (six,))
    else:
      # If we were unable to find the code in servers, we log it as a warning
      logger.log(f'Recieved remove request for code({roomcode}), however requested row is not present in servers table, aborting...', 2)
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while removing a server; Error message: {e}; Data: {(roomcode)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while removing a user; Error message: {e}')
  db.commit()
  return True


# Return serverID, name, owner
def getServerInfo(roomcode: str) -> tuple[int, str, int]:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    res = cursor.execute('SELECT id, name, owner FROM servers WHERE code = ?', (roomcode,))
    res = res.fetchone()
    db.commit()
    if res:
      return res[0], res[1], res[2]
    logger.log(f'Server id for {roomcode} not present!')
    return -1, '', -1
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while getting serverId name; Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting serverId name; Error message: {e}')
  db.commit()
  return -1, '', -1


def getServerId(roomcode: str) -> int:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    res = cursor.execute('SELECT id FROM servers WHERE code = ?', (roomcode,))
    res = res.fetchone()
    db.commit()
    if res:
      return res[0]
    logger.log(f'Server id for {roomcode} not present!')
    return -1
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while getting serverId; Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting serverId; Error message: {e}')
  db.commit()
  return -1


# Message format: {'message': '', 'sender': '', 'time': ''}
def addMessage(roomcode: str, message: dict) -> bool:
  try:
    if (not checkIfCodeExists(roomcode)):
      logger.log(f'Roomcode {roomcode} not present!', 2)
      return False
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    ix = getServerId(roomcode)
    cursor.execute('INSERT INTO messages(message, sender, time, serverId) VALUES(?, ?, ?, ?);', (message['message'], message['sender'], message['time'], ix))
    res = cursor.execute('SELECT id FROM messages WHERE serverId = ? ORDER BY id ASC;', (ix,))
    res = res.fetchall()
    if len(res) > 100:
      cursor.execute('DELETE FROM messages WHERE id = ?', (res[0][0],))
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while adding message; Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while adding message; Error message: {e}')
  db.commit()
  return True


# Return message, sender, time
def getMessages(roomcode: str) -> list[tuple[str, str, str]]:
  try:
    if (not checkIfCodeExists(roomcode)):
      logger.log(f'Roomcode {roomcode} not present!', 2)
      return False
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    ix = getServerId(roomcode)
    res = cursor.execute('SELECT message, sender, time FROM messages WHERE serverId = ? ORDER BY id ASC;', (ix,))
    res = res.fetchall()
    db.commit()
    if res:
      return res
    return []
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while getting messages; Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting messages; Error message: {e}')
  db.commit()
  return []


def userJoinServer(uix: int, roomcode: str) -> bool:
  try:
    if (not checkIfCodeExists(roomcode)):
      logger.log(f'Roomcode {roomcode} not present!', 2)
      return False
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    six = getServerId(roomcode)
    if not isUserInServer(uix, six):
      cursor.execute('INSERT INTO userServerMember(userId, serverId) VALUES (?, ?)', (uix, six))
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while user({uix}) tried joining server({six}); Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while user({uix}) tried joining server({six}); Error message: {e}')
  db.commit()
  return True


def userLeaveServer(uix: int, roomcode: str) -> True:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    six = getServerId(roomcode)
    if isUserInServer(uix, six):
      cursor.execute('DELETE FROM userServerMember WHERE userId = ? AND serverId = ?', (uix, six))
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while removing user server relation; Error message: {e}; Data: {(uix, roomcode)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while removing user server relation; Error message: {e}')
  db.commit()
  return True


def isUserInServer(uix: int, six: int) -> bool:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    # If username is in users
    res1 = cursor.execute('SELECT id FROM userServerMember WHERE userId = ? AND serverId = ?;', (uix, six))
    res1 = res1.fetchall()
    db.commit()
    if res1:
      return True
    return False
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while checking if a user server relation already exists; Error message: {e}; Data: {(uix, six)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while checking if a user server relation already exists; Error message: {e}')
  db.commit()
  return True


def isServerOwner(uix: int, roomcode: str) -> bool:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    res = cursor.execute('SELECT owner FROM servers WHERE code = ?', (roomcode,))
    res = res.fetchone()
    db.commit()
    if res:
      return res[0] == uix
    logger.log(f'Server id for {roomcode} not present!')
    return False
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while checking if user({uix}) is owner of server({roomcode}); Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while checking if user({uix}) is owner of server({roomcode}); Error message: {e}')
  db.commit()
  return False


def getUixFromUsername(username: str) -> int:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    # If username is in users
    res1 = cursor.execute('SELECT id FROM users WHERE username = ?;', (username,))
    res1 = res1.fetchall()
    db.commit()
    return res1
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while getting uix from username; Error message: {e}; Data: {(username)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting uix from username; Error message: {e}')
  db.commit()
  return -1


def changeServerOwner(newOwnerName: str, roomcode: str) -> bool:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    ownerix = getUixFromUsername(newOwnerName)
    if ownerix == -1:
      return False
    cursor.execute('UPDATE servers SET owner=? WHERE roomcode = ?;', (ownerix, roomcode))
    db.commit()
    return True
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while changing server owner; Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while changing server owner; Error message: {e}')
  db.commit()
  return False


def eraseServerHistory(roomcode: str) -> True:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    six = getServerId(roomcode)
    if six == -1: logger.log(f'Trying to erase from nonexistent server (code: {roomcode})', 2)
    cursor.execute('DELETE FROM messages WHERE serverId = ?', (six,))
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while erasing server history; Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while erasing server history; Error message: {e}')
  db.commit()
  return True


def getUserServers(uix: int) -> list[tuple[str, str]]:
  try:
    db = sqlite3.connect(DBLOCATION)
    cursor = db.cursor()
    res = cursor.execute('SELECT servers.name, servers.code FROM servers INNER JOIN userServerMember ON userServerMember.serverId=servers.id WHERE userServerMember.userId=?', (uix,))
    res = res.fetchall()
    return res
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while getting user servers; Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting user servers; Error message: {e}')
  db.commit()
  return []


#REMOVE FROM FINAL VERSION
def selectall(): # Used for displaying data REMOVE FROM FINAL VERSION
  db = sqlite3.connect(DBLOCATION) #REMOVE FROM FINAL VERSION
  cursor = db.cursor()#REMOVE FROM FINAL VERSION
  res1 = cursor.execute('SELECT * FROM users;')#REMOVE FROM FINAL VERSION
  res1 = res1.fetchall()#REMOVE FROM FINAL VERSION
  db.commit()#REMOVE FROM FINAL VERSION
  return res1#REMOVE FROM FINAL VERSION
#REMOVE FROM FINAL VERSION
