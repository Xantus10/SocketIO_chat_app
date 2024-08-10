from datetime import datetime


class Logger:
  def __init__(self):
    self.CONFIG = {}
    self.CONFIG['OUTPUT_FILE'] = 'data/log.txt'
    # Default: 0 - all, otherwise the log level should be 1 lower than priority passed to log() - to log only Error(3) and above LOG_LEVEL should be 2
    self.CONFIG['LOG_LEVEL'] = 0

  # 1-3 for Message (*), Warning (#), Error (!)
  def log(self, msg: str, ptype=3):
    try:
      if ptype < self.CONFIG['LOG_LEVEL']: return
      # Identificators for messages ([*], [!], etc.)
      if ptype == 1:
        descriptionChar = '*'
      elif ptype == 2:
        descriptionChar = '#'
      elif ptype == 3:
        descriptionChar = '!'
      else:
        # Use [U] for Unidentified logs
        descriptionChar = 'U'
      # Format the log Into: [ID] (date time) - message with newlines replaced with ;;
      toLog = f'[{descriptionChar}] ({datetime.now().strftime("%d.%m.%Y %H:%M:%S")}) - {msg.replace(chr(10), ";;")}{chr(10)}'
      # Write to logfile
      with open('data/log.txt', 'a') as f:
        f.write(toLog)
        f.close()
    except Exception as e:
      print(f'ERROR Unexpected Exception occurred while logging: {e}\nPLEASE RESOLVE IMMEDIATLY')
