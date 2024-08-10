from hashlib import sha256
from base64 import b64encode, b64decode
from secrets import token_hex
from json import loads, dumps


class JWT:
  #a$4 B1^*nP+**w-b(Y1{BTr-!uIr56]s/Be*#q8-e@VdsZ4H&3 Ea7*yr)1aE}e*5-yGg4e`sg"4r\'86g>~s4|
  def __init__(self):
    self.JWT_DATA = {}
    self.JWT_DATA['SECRET_KEY'] = 'JWT_SECRET_KEY'
    self.JWT_DATA['USER_CONTEXT_LEN'] = 32


  # Create a jwt token from data and self.JWT_DATA['SECRET_KEY']; return jwt_token,user_context_plain
  def jwtencode(self, data: dict):
    user_context = token_hex(self.JWT_DATA['USER_CONTEXT_LEN'])
    data['user_context'] = sha256(bytes(user_context, 'utf-8')).hexdigest()
    str_data = dumps(data)
    signature = sha256(bytes(str_data + self.JWT_DATA['SECRET_KEY'], 'utf-8')).hexdigest()
    return b64encode(bytes(str_data, 'utf-8')).decode('utf-8') + '.' + b64encode(bytes(signature, 'utf-8')).decode('utf-8'), user_context


  def checkSignature(self, data: str, sig: str):
    check = sha256(bytes(data + self.JWT_DATA['SECRET_KEY'], 'utf-8')).hexdigest()
    return sig == check


  def checkUserContext(self, orig: str, uhash: str):
    return sha256(bytes(orig, 'utf-8')).hexdigest() == uhash


  # Decode and validate jwt token; return bool_isValid,dict_data
  def jwtdecode(self, token: str, user_context: str):
    data, sig = token.split('.')
    data = b64decode(data.encode('utf-8')).decode('utf-8')
    sig = b64decode(sig.encode('utf-8')).decode('utf-8')
    check = self.checkSignature(data, sig)
    if not check:
      return False, {'fail_msg': 'Failed signgature check'}
    data = loads(data)
    check = self.checkUserContext(user_context, data['user_context'])
    if not check:
      return False, {'fail_msg': 'Failed user context check'}
    return True, data


  def set_secret_key(self, key: str):
    self.JWT_DATA['SECRET_KEY'] = key


##j = JWT()
##j.JWT_DATA['SECRET_KEY'] = 'aaaa'
##t, uc = j.jwtencode({'name': 'user123', 'priv': 2})
##print(t)
##print(uc)
##b, d = j.jwtdecode(t, uc)
##print(b)
##print(d)
