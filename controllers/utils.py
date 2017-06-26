import datetime

GRACE_PERIOD = 10


def heartbeat():
    if 'playtime' in request.env.http_referer:
        now = datetime.datetime.now()
        db((db.playtime.status == IN_PROGRESS)).update(heartbeat=now)
        response = dict(status='OK', last_heartbeat=str(now))
    else:
        response = dict(status='ERROR', last_heartbeat=None)

    return str(response)


def countdown():
    if session.playtime is None or session.playtime.session_id is None:
        return dict(status='ERROR')

    if session.playtime.checkpoint is None:
        play_session = db(db.playtime.id == session.playtime.session_id).select(db.playtime.next_checkpoint).first()
        session.playtime.checkpoint = play_session.next_checkpoint

    delta = session.playtime.checkpoint - datetime.datetime.now()
    if delta.days == 0 and delta.seconds != 0:
        return dict(sec_left=delta.seconds)
    else:
        play_session = db(db.playtime.id == session.playtime.session_id).select(db.playtime.config).first()
        delta = datetime.timedelta(seconds=play_session.config.runtimer + GRACE_PERIOD)
        next = datetime.datetime.now() + delta
        db(db.playtime.id == session.playtime.session_id).update(next_checkpoint=next)
        session.playtime.checkpoint = next
        return dict(sec_left=0, overdue=True)

def mysession():
    return dict()