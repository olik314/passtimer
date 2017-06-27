import random, string
import datetime

_DELTA = datetime.timedelta(seconds=10)


def generateToken(salt, moment=None):
    if moment is None:
        moment = datetime.datetime.now()
    slice = moment.replace(second=(moment.second / 10) * 10, microsecond=0)
    random.seed(str(slice) + salt)
    token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

    return token


def validateToken(token, salt):
    two_factor = list()
    now = datetime.datetime.now()

    for moment in [now - _DELTA, now, now + _DELTA]:
        two_factor.append(generateToken(salt, moment))

    if token in two_factor:
        return True
    else:
        return False