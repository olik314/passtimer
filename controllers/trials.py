import random

trial_list = [
    'regular',
    'regularmasked'
]

_SALT = 'thereisabootinmysnek'

def index():
    if session.playtime is None or session.playtime.session_id is None:
        return dict(status='ERROR', trial='ERROR: Trial couldn\'t be retrieved' )

    session_id = session.playtime.session_id

    play_session = db((db.playtime.id == session_id) & (db.playtime.status == IN_PROGRESS)).select(
        db.playtime.next_checkpoint, db.playtime.stats).first()

    if play_session is None:
        return dict(status='ERROR', trial='ERROR: Trial couldn\'t be retrieved')

    checkpoint = play_session.next_checkpoint
    start = play_session.stats.start_time
    delta = checkpoint - start

    random.seed(str(delta) + _SALT)
    choice = random.choice(trial_list)

    return dict(trial=LOAD(url=URL(r=request, c='trials', f='{}.load'.format(choice)), ajax=True,
                           content=IMG(_src=URL('static/images', 'preloader.gif'))))


def regular():
    return dict()


def regularmasked():
    return dict()


def validate():
    return dict()
