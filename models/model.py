import uuid

db.define_table('playtime_config',
                Field('runtimer', type='integer', requires=IS_NOT_EMPTY(), notnull=True),
                Field('num_password', type='integer', requires=IS_INT_IN_RANGE(9, 256)),
                Field('password_percent', type='double', notnull=True, requires=IS_FLOAT_IN_RANGE(-1, 101)),
                Field('use_fake', type='boolean', notnull=True, default=False),
                Field('fake_percent', type='double', requires=IS_FLOAT_IN_RANGE(-1, 51)),
                Field('use_events', type='boolean', notnull=True, default=False),
                Field('event_percent', type='double', requires=IS_FLOAT_IN_RANGE(-1, 101)))

db.define_table('playtime_stats',
                Field('start_time', type='datetime'),
                Field('end_time', type='datetime'),
                Field('final_title', type='string'),
                Field('average_time', type='double', default=0.0),
                Field('mistakes', type='integer', default=0))

db.define_table('playtime_release',
                Field('image', 'upload', uploadfield='image_file'),
                Field('image_file', 'blob'))

db.define_table('playtime',
                Field('in_progress', type='boolean', notnull=True, default=True),
                Field('uuid', 'string', length=64, default=lambda: str(uuid.uuid4())),
                Field('config', 'reference playtime_config', notnull=True),
                Field('stats', 'reference playtime_stats', notnull=True),
                Field('image', 'reference playtime_release', notnull=True),
                Field('generated_passwords', type='boolean', notnull=True, default=False))

db.define_table('passwords',
                Field('playtime', type='reference playtime'),
                Field('md5', type='string', length=32),
                Field('validated', type='boolean', default=False),
                primarykey=['playtime','md5'])