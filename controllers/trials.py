import random

trial_list = [
    'regular',
    'regularmasked'
]


def index():
    choice = random.SystemRandom().choice(trial_list)
    return dict(trial=LOAD(url=URL(r=request, c='trials', f='{}.load'.format(choice)), ajax=True,
                           content=IMG(_src=URL('static/images', 'preloader.gif'))))


def regular():
    return dict()


def regularmasked():
    return dict()

def regulartall():
    return dict()


def validate():
    return dict()
