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
    logger.log('An error in SQL syntax occurred while initializing tables')
  except Exception as e:
    logger.log(f'An unexpected error occurred while initializing tables; Error message: {e}')
  db.commit()
  return True


def checkIfCodeExists(roomcode: str):
  pass


def checkIfServerExists(roomcode: str):
  pass


def removeServer(roomcode: str):
  pass


def getServerId(roomcode: str):
  pass


def addMessage(roomcode: str, message: str):
  pass


def getMessages(roomcode: str):
  pass

#REMOVE FROM FINAL VERSION
def selectall(): # Used for displaying data REMOVE FROM FINAL VERSION
  db = sqlite3.connect('data/database.db') #REMOVE FROM FINAL VERSION
  cursor = db.cursor()#REMOVE FROM FINAL VERSION
  res1 = cursor.execute('SELECT * FROM users;')#REMOVE FROM FINAL VERSION
  res1 = res1.fetchall()#REMOVE FROM FINAL VERSION
  db.commit()#REMOVE FROM FINAL VERSION
  return res1#REMOVE FROM FINAL VERSION
#REMOVE FROM FINAL VERSION
