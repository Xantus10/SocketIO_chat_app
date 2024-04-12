import sqlite3
from secrets import token_hex

import logs as logger


# Reset the database
def reset():
  pass


# Initialize all database tables
def initialize():
  try:
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    # Table for users
    cursor.execute('CREATE TABLE IF NOT EXISTS servers(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, code TEXT NOT NULL UNIQUE);')
    cursor.execute('CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT NOT NULL, serverId INTEGER NOT NULL, CONSTRAINT FK_serverId FOREIGN KEY(serverId) REFERENCES servers(id));')
  except sqlite3.Error as e:
    logger.log('An error in SQL syntax occurred while initializing tables')
  except Exception as e:
    logger.log(f'An unexpected error occurred while initializing tables; Error message: {e}')
  db.commit()
  return True


def addServer(name: str, roomcode: str):
  try:
    if (checkIfCodeExists(roomcode)):
      logger.log(f'Roomcode {roomcode} already exists!', 2)
      return False
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    # Table for users
    cursor.execute('INSERT INTO servers(name, code) VALUES(?, ?);', (name, roomcode))
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while adding server; Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while adding server; Error message: {e}')
  db.commit()
  return True


def checkIfCodeExists(roomcode: str):
  try:
    db = sqlite3.connect('data/database.db')
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


def removeServer(roomcode: str):
  try:
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    # Find a user
    srv = cursor.execute('SELECT * FROM servers WHERE code = ?;', (roomcode,))
    srv = srv.fetchone()
    if srv:
      cursor.execute('DELETE FROM servers WHERE code = ?', (roomcode,))
    else:
      # If we were unable to find the code in servers, we log it as a warning
      logger.log(f'Recieved remove request for code({roomcode}), however requested row is not present in servers table aborting', 2)
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while removing a server; Error message: {e}; Data: {(roomcode)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while removing a user; Error message: {e}')
  db.commit()
  return True


def getServerId(roomcode: str):
  try:
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    # Table for users
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


def addMessage(roomcode: str, message: str):
  try:
    if (not checkIfCodeExists(roomcode)):
      logger.log(f'Roomcode {roomcode} not present!', 2)
      return False
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    ix = getServerId(roomcode)
    cursor.execute('INSERT INTO messages(message, serverId) VALUES(?, ?);', (message, ix))
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while adding message; Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while adding message; Error message: {e}')
  db.commit()
  return True


def getMessages(roomcode: str):
  try:
    if (not checkIfCodeExists(roomcode)):
      logger.log(f'Roomcode {roomcode} not present!', 2)
      return False
    db = sqlite3.connect('data/database.db')
    cursor = db.cursor()
    ix = getServerId(roomcode)
    res = cursor.execute('SELECT message FROM messages WHERE serverId = ? ORDER BY message ASC;', (ix,))
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

#REMOVE FROM FINAL VERSION
def selectall(): # Used for displaying data REMOVE FROM FINAL VERSION
  db = sqlite3.connect('data/database.db') #REMOVE FROM FINAL VERSION
  cursor = db.cursor()#REMOVE FROM FINAL VERSION
  res1 = cursor.execute('SELECT * FROM users;')#REMOVE FROM FINAL VERSION
  res1 = res1.fetchall()#REMOVE FROM FINAL VERSION
  db.commit()#REMOVE FROM FINAL VERSION
  return res1#REMOVE FROM FINAL VERSION
#REMOVE FROM FINAL VERSION
