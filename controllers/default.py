# -*- coding: utf-8 -*-
from gluon.storage import Storage
import math, random, string
import hashlib
import datetime
from randomsalt import SaltyCracker

# Possible statuses for playtime:
READY = 'READY'
IN_PROGRESS = 'IN_PROGRESS'
STANDBY = 'STANDBY'
STARTED = 'STARTED'
COMPLETED = 'COMPLETED'
STOPPED = 'STOPPED'

_sc = SaltyCracker()
KEY = _sc.getSecret()
SALT = _sc.getSalt()

def index():
    if session.playtime is None:
        session.playtime = Storage()
    return dict()


def config():
    if session.playtime is None:
        db((db.playtime.status == IN_PROGRESS) | (db.playtime.status == STANDBY)).update(status=STOPPED)
        session.playtime = Storage()
    elif session.playtime.session_id is not None:
        db(((db.playtime.status == IN_PROGRESS) | (db.playtime.status == STANDBY)) & (
            db.playtime.id != session.playtime.session_id)).update(
            status=STOPPED)
        redirect(URL('index'))
    else:
        db((db.playtime.status == IN_PROGRESS) | (db.playtime.status == STANDBY)).update(status=STOPPED)

    form = SQLFORM.factory(
        Field('release', type='upload', uploadfield='image_file', label='Release image',
              requires=[IS_NOT_EMPTY(error_message='You must provide a picture!'),
                        IS_IMAGE(extensions=('jpeg', 'png'), error_message='Only JPG and PNG supported')]),
        Field('runtimer', type='integer', label='Countdown timer duration', comment='(in seconds)',
              requires=IS_NOT_EMPTY(), default=60),
        Field('use_time_limit', type='boolean', label='Set maximum session time', default=False),
        Field('time_limit', label='Maximum session time', default=16200),
        Field('num_password', type='integer', label='Generate # passwords', requires=IS_NOT_EMPTY(), default=30),
        Field('password_percent', type='integer', label='Password percentage needed for release',
              requires=IS_NOT_EMPTY(), default=100),
        Field('use_fake', type='boolean', label='Activate fake passwords', default=False),
        Field('fake_percent', type='integer', label='Percentage of fake passwords',
              requires=IS_INT_IN_RANGE(-1, 51), default=10),
        Field('use_events', type='boolean', label='Activate random events', default=False),
        Field('event_percent', type='integer', label='Chance of firing a random event',
              requires=IS_INT_IN_RANGE(-1, 101), default=20),
        table_name='config')
    vars = None
    if form.process().accepted:
        vars = request.vars

        config_id = db.playtime_config.insert(runtimer=vars.runtimer, num_password=vars.num_password,
                                              password_percent=vars.password_percent,
                                              use_fake=vars.use_fake or False,
                                              fake_percent=vars.fake_percent if vars.use_fake else None,
                                              use_events=vars.use_events or False,
                                              event_percent=vars.event_percent if vars.use_events else None,
                                              has_limit=vars.use_time_limit or False,
                                              time_limit=datetime.datetime.now() + datetime.timedelta(
                                                  seconds=int(vars.time_limit)) if vars.use_time_limit else None)
        stats_id = db.playtime_stats.insert()
        release_id = db.playtime_release.insert(image=db.playtime_release.image.store(vars.release),
                                                image_file=vars.release.value)
        session_id = db.playtime.insert(config=config_id, stats=stats_id, image=release_id)

        session.playtime.session_id = session_id

        redirect(URL('genpasswords'))

    elif form.errors:
        response.flash = 'Form has errors'
    else:
        response.flash = ''

    return dict(form=form, vars=vars)


def genpasswords():
    if session.playtime is None:
        redirect(URL('index'))

    session_id = session.playtime.session_id
    play_session = db((db.playtime.id == session_id) & (db.playtime.status == READY)).select().first()

    if play_session is None:
        redirect(URL('index'))
    elif play_session.status == STANDBY:
        redirect(URL('index'))

    def genPasswd(length=10):
        return ''.join(
            random.SystemRandom().choice(string.ascii_letters + string.digits + '!$%#@?&-_') for _ in range(length))

    config = play_session.config

    password_list = list()
    for _ in range(config.num_password):
        password_list.append(genPasswd())

    for password in password_list:
        md5 = hashlib.md5()
        md5.update(password)
        db.passwords.insert(playtime=session_id, md5=md5.hexdigest())
    db(db.playtime.id == session_id).update(status=STANDBY)
    db(db.playtime_stats.id == play_session.stats.id).update(start_time=datetime.datetime.now())

    if config.fake_percent is not None:
        fake_proportion = config.fake_percent / 100.0
        additional_fake = int(math.ceil(config.num_password * fake_proportion))
        for _ in range(additional_fake):
            password_list.append(genPasswd())

    random.shuffle(password_list)

    return dict(passwords=password_list, seclink=URL('playtime'))


def playtime():
    if session.playtime is None:
        redirect(URL('index'))

    now = datetime.datetime.now()
    countdown = 0

    session_id = session.playtime.session_id
    if session.playtime.started:
        play_session = db((db.playtime.id == session_id) & (db.playtime.status == IN_PROGRESS)).select().first()
        delta = play_session.next_checkpoint - now

        if delta.days == 0:
            countdown = delta.seconds

    else:
        play_session = db((db.playtime.id == session_id) & (db.playtime.status == STANDBY)).select().first()

        if play_session is None:
            redirect(URL('index'))

        delta = datetime.timedelta(seconds=play_session.config.runtimer)
        db(db.playtime.id == session_id).update(status=IN_PROGRESS, heartbeat=now, next_checkpoint=now + delta)
        session.playtime.started = True
        countdown = delta.seconds

    return dict(play_session=play_session, countdown=countdown, trial='',
                seclink=URL('utils', 'heartbeat', hmac_key=KEY, salt=SALT))


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
