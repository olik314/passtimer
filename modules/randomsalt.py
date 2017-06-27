import random, string

_SALT = None
_SECRET = None


class SaltyCracker(object):
    def __init__(self):
        global _SALT
        global _SECRET

        if _SALT == None:
            _SALT = ''.join(random.SystemRandom().choice(string.ascii_letters) for _ in range(8))
        if _SECRET == None:
            _SECRET = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))

    def getSecret(self):
        return _SECRET

    def getSalt(self):
        return _SALT
