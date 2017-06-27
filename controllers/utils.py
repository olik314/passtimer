import datetime
import time
from randomsalt import SaltyCracker

GRACE_PERIOD = 10

_sc = SaltyCracker()
KEY = _sc.getSecret()
SALT = _sc.getSalt()

def heartbeat():
    if 'playtime' in request.env.http_referer and URL.verify(request, hmac_key=KEY, salt=SALT):
        now = datetime.datetime.now()
        db((db.playtime.status == IN_PROGRESS)).update(heartbeat=now)
        response = dict(status='OK', last_heartbeat=str(now))
    else:
        response = dict(status='ERROR', last_heartbeat=None)

    return str(response)


def resync():
    if session.playtime is None or session.playtime.session_id is None:
        return dict(status='ERROR')

    if session.playtime.checkpoint is None:
        play_session = db(db.playtime.id == session.playtime.session_id).select(db.playtime.next_checkpoint).first()
        session.playtime.checkpoint = play_session.next_checkpoint

    delta = session.playtime.checkpoint - datetime.datetime.now()
    if delta.days == 0 and delta.seconds != 0:
        return dict(next_checkpoint=time.mktime(session.playtime.checkpoint.timetuple())*1000, status='OK')
    else:
        play_session = db(db.playtime.id == session.playtime.session_id).select(db.playtime.config).first()
        delta = datetime.timedelta(seconds=play_session.config.runtimer + GRACE_PERIOD)
        next = datetime.datetime.now() + delta
        db(db.playtime.id == session.playtime.session_id).update(next_checkpoint=next)
        session.playtime.checkpoint = next
        return dict(next_checkpoint=time.mktime(session.playtime.checkpoint.timetuple())*1000, status='OVERDUE')

def mysession():
    return dict()