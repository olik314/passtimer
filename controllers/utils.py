import datetime

def heartbeat():
    db((db.playtime.generated_passwords == True) & (db.playtime.started == True)).update(heartbeat=datetime.datetime.now())
    return str(dict(beep='BOOP!'))