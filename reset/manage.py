# -- coding: UTF-8 --

import os
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell, prompt_bool

from app import create_app, db
from app.models import Permission, Role, User, Group, AimExUser, Tablecol
from sqlalchemy import text
from app.mondb_models import *

from app.logic.user_logic import create_user
from app.foundation import log
import json
from time import time
import shutil
import signal
from flask.ext.alchemydumps import AlchemyDumpsCommand

# app = create_app('release')
app = create_app('release')
nowpath = os.path.split(os.path.realpath(__file__))[0]
# logging.basicConfig(filename='%s/error.log'%nowpath, level=logging.ERROR)
manager = Manager(app)
migrate = Migrate(app, db)


def back_up_mongo_data():
    from config import Config
    import datetime
    log.info("back up mongo db")
    dbinfo = Config.MONGOINFO
    databaseip = dbinfo['ip']
    dbport = dbinfo['port']
    authdb = dbinfo['authdb']
    database = dbinfo['db']
    username, password = dbinfo['username'], dbinfo['password']
    databaseip = databaseip if databaseip else "127.0.0.1"
    t = datetime.datetime.now()
    seven_day_ago = t - datetime.timedelta(days=4)
    unpackdate = t.strftime('%Y%m%d-%H%M') + "-m"
    unpackdate_seven_ago = seven_day_ago.strftime('%Y%m%d-%H%M')
    backup_path = "/backup/mongo/" + unpackdate
    mongo_dump_command = "/usr/bin/mongodump -h %s --port %s --authenticationDatabase %s -u %s -p %s -o %s" % (
        databaseip, dbport, authdb, username, password, backup_path)
    log.info(mongo_dump_command)
    res = os.system(mongo_dump_command)
    log.info(res)
    remove_command = "rm -rf " + "/backup/mongo/" + unpackdate_seven_ago
    res = os.system(remove_command)
    log.info(res)


def make_shell_context():
    return dict(
            app=app,
            db=db,
            mondb=mondb,
            Permission=Permission,
            Role=Role,
            User=User,
            Tablecol=Tablecol,
            Group=Group,
            AimExUser=AimExUser,
            phoneplan=phoneplan,
            phoneresinfo=phoneresinfo,
            aismangerinfo=aismangerinfo,
            callschedule=callschedule,
            sipserverinfo=sipserverinfo,
            api_authentication=api_authentication,
            recordfileinfo=recordfileinfo,
            templates=templates,
            callStrategy=callStrategy,
            calltime=calltime,

            # Add models here...
    )


from pymongo import ASCENDING, DESCENDING
import mongoengine
from mongoengine.connection import get_db


def connect():
    mongoengine.connect('yfsrobot', host='127.0.0.1', port=27017, username='yfsrobot', password='yfsrobotksdw1212')


@manager.command
def delete_alembic():
    sql = text('DROP TABLE alembic_version;')
    db.engine.execute(sql)


@manager.command
def clear_aiport():
    sql = text('delete from aiports;')
    db.engine.execute(sql)


@manager.command
def getuserid(username):
    likename = "%" + username + "%"
    users = db.session.query(User).filter(User.username.like(likename)).all()
    user_ids = []
    for user in users:
        log.info("%d : %s: %d" % (user.id, user.username, user.inc_id))
        user_ids.append(user.id)
    return user_ids


@manager.option('-u', '--username', dest='username', default='admin')
@manager.option('-p', '--password', dest='password', default="Sdftd11")
@manager.option('-e', '--email', dest='email', default="noreply@lsrobot.vip")
@manager.option('-i', '--inc_name', dest='inc_name', default="shengxun")
@manager.option('-m', '--phone', dest='phone', default="15088777656")
@manager.option('-n', '--ai_num', dest='ai_num', default=1, type=int)
@manager.option('-o', '--aim_sn', dest='aim_sn', default="")
@manager.option('-q', '--money', dest='money', default=1000000.0, type=float)
@manager.option('-r', '--active', dest='active', default=True, type=bool)
@manager.option('-s', '--confirmed', dest='confirmed', default=True, type=bool)
def create_e_user(username, password, email, inc_name, phone, ai_num=1,
                  aim_sn="", money=1000000.0, active=True, confirmed=True):
    create_user(email=email,
                username=username,
                password=password,
                # name=form.name.data,  # 姓名
                inc_name=inc_name,  # 公司名
                # position=form.position.data,  # 职位
                phone=phone,  # 电话
                ai_num=ai_num,
                aim_sn=aim_sn,
                money=money,
                active=active,
                confirmed=confirmed
                )
    db.session.commit()


from app.common import sfm_to_seconds


@manager.command
def set_during():
    plans = phoneplan.objects(is_delete=False)

    for plan in plans:
        if "phoneprocessinfo" in plan.current_phoneres:
            during = sfm_to_seconds(plan.current_phoneres["phoneprocessinfo"]["time"])
            plan.update(set__current_phoneres__during=during)


@manager.command
def restore_deleted(userid):
    datas1 = json.loads(phoneplan.objects(owner=userid, is_delete=True).only("id").to_json())

    for data in datas1:
        try:
            phoneplan.objects(id=data['_id']['$oid']).update(is_delete=False)
        except Exception as e:
            log.exception(e)


@manager.command
def complete_plan(userid):
    ABCD = ["A", "B", "C", "D"]
    is_dial = [0, 1]
    datas1 = json.loads(phoneplan.objects(owner=userid,
                                          current_phoneres__phoneprocessinfo__restag__in=ABCD,
                                          isdial__in=is_dial,
                                          is_delete=False).only("id").to_json())
    if prompt_bool("Are you sure ? You will update %d of datas!" % len(datas1)):
        for data in datas1:
            try:
                phoneplan.objects(id=data['_id']['$oid']).update(isdial=2, status=2)
            except Exception as e:
                log.exception(e)


@manager.command
def reset_getnumbered(userid):
    ABCD = ["A", "B", "C", "D"]
    is_dial = [1]
    current_time = int(time())
    ten_mins_ago = current_time - 60 * 10
    datas1 = json.loads(phoneplan.objects(owner=userid,
                                          current_phoneres__phoneprocessinfo__restag__nin=ABCD,
                                          status=1,
                                          isdial__in=is_dial,
                                          updatetime__lte=ten_mins_ago,
                                          is_delete=False).only("id").to_json())
    if prompt_bool("Are you sure ? You will update %d of datas!" % len(datas1)):
        for data in datas1:
            try:
                phoneplan.objects(id=data['_id']['$oid']).update(isdial=1, status=0)
            except Exception as e:
                log.exception(e)


@manager.command
def mv_recordfile(userid):
    pagination = recordfileinfo.objects(uid=int(userid), user='db').paginate(1, 1000)
    page = pagination.pages
    init_path = "/data/recodedata/recordfile_bk_11/"
    continue_move = True

    def _stop(_sig=None, _stack=None):
        print("Do some clean up job. PLEASE be patient...")
        continue_move = False

    signal.signal(
            signal.SIGINT, _stop
    )

    for i in range(page):
        t = i + 1
        if not continue_move:
            break
        pagination = recordfileinfo.objects(uid=int(userid), user='db')
        for recordfile in pagination:
            if not continue_move:
                break
            if hasattr(recordfile, 'unpackdate') and \
                            recordfile.unpackdate is not None \
                    and "-" not in recordfile.unpackdate:
                continue
            print(recordfile)
            # print(type(recordfile))
            filename = recordfile.file
            micon = recordfile.micon
            time = recordfile.time[:10]
            dist_path = "%s%s/%s" % (init_path, time, micon)
            src_path = init_path + micon
            if not os.path.exists('%s%s' % (init_path, time)):
                mkdir_command = 'mkdir %s%s' % (init_path, time)
                os.system(mkdir_command)
            try:
                print('mv {} {} \n'.format(src_path, dist_path))
                if not os.path.exists(src_path):
                    continue
                shutil.move(src_path, dist_path)
                recordfile.update(unpackdate=time)
                recordfileinfo.objects(micon=micon).update(unpackdate=time)
            except Exception as e:
                print(e)
                continue


@manager.command
def back_up_db():
    back_up_mongo_data()


@manager.command
def delete_unused_data():
    keep_time = int(time()) - 120 * 24 * 60 * 60  # 75天
    delete_time = int(time()) - 20 * 24 * 60 * 60  # 20天

    phoneplan_count = phoneplan.objects(current_phoneres__lastime__lte=int(keep_time),
                                        current_phoneres__lastime__ne=None).count()
    log.info("total deleted phoneplan count: " + str(phoneplan_count))
    if prompt_bool("Are you sure ? You will delete %d of datas!" % phoneplan_count):
        phoneplan.objects(current_phoneres__lastime__lte=int(keep_time), current_phoneres__lastime__ne=None).delete()

    phonesinfos = phoneresinfo.objects(lastime__lte=int(keep_time)).order_by('id')[0:5000]
    all_count = 0
    last_id = None

    while phonesinfos:
        phoneinfo_ids = [phonesinfo.id for phonesinfo in phonesinfos]
        plan_ids = [phonesinfo.planid for phonesinfo in phonesinfos]
        plan_ids_map = {}
        for phonesinfo in phonesinfos:
            plan_ids_map[phonesinfo.planid] = phonesinfo.id
        need_plan_ids = json.loads(phoneplan.objects(id__in=plan_ids, is_delete=False).only("id").to_json())
        need_plan_ids = [x['_id']['$oid'] for x in need_plan_ids]
        log.info("need plan " + str(len(need_plan_ids)))
        unused_id = set(plan_ids) - set(need_plan_ids)
        log.info("unused_id plan " + str(len(unused_id)))
        unused_phones_ids = [plan_ids_map[x] for x in unused_id]

        new_phonesinfos = phoneresinfo.objects(id__in=unused_phones_ids)
        micons = [phonesinfo.micon for phonesinfo in new_phonesinfos]
        del_id_count = len(unused_phones_ids)
        all_count = all_count + del_id_count
        log.info("delete " + str(del_id_count))
        phoneresinfo.objects(id__in=unused_phones_ids).delete()
        calltime.objects(resid__in=unused_phones_ids).delete()
        recordfileinfo.objects(micon__in=micons).delete()
        last_id = phoneinfo_ids[:-1][0]
        log.info("last id: " + str(last_id))
        phonesinfos = phoneresinfo.objects(id__gt=last_id, lastime__lte=int(keep_time))[0:5000]

    log.info("total deleted phonesinfos count: " + str(all_count))


@manager.command
def mv_all_recordfile():
    user_ids = getuserid("")
    for user_id in user_ids:
        mv_recordfile(user_id)
        log.info("move user " + str(user_id) + " complete")


@manager.command
def create_indexes():
    connect()
    db = get_db()

    aismanagerinfoi = db['aismanagerinfo']
    aismanagerinfoi.ensure_index([('mac', ASCENDING)], background=True)

    phoneplani = db['phoneplan']
    phoneplani.ensure_index([('owner', ASCENDING), ('is_delete', ASCENDING),
                             ('isdial', ASCENDING), ('clash', ASCENDING),
                             ('current_phoneres.phoneprocessinfo.restag', ASCENDING),
                             ('current_phoneres.lastime', ASCENDING),
                             ('addprivatetime', ASCENDING),
                             ('uptime', ASCENDING),
                             ('sort_id', DESCENDING)],
                            background=True, name='phoneplanall')

    phoneplan.ensure_index([('owner', ASCENDING), ('phonenumber', ASCENDING),
                            ('isdial', ASCENDING),
                            ('current_phoneres.phoneprocessinfo.restag', ASCENDING),
                            ('current_phoneres.lastime', ASCENDING),
                            ('is_delete', ASCENDING)],
                           background=True, name='phoneplan_tag_index')

    phoneplani.ensure_index([('isdial', ASCENDING), ('status', ASCENDING),
                             ('owner', ASCENDING), ('localphone', ASCENDING),
                             ('is_delete', ASCENDING)], background=True)

    phoneplani.ensure_index([('owner', ASCENDING), ('isdial', ASCENDING)],
                            background=True)
    phoneplani.ensure_index([('status', ASCENDING), ('owner', ASCENDING),
                             ('isdial', ASCENDING)], background=True)
    phoneplani.ensure_index([('isdial', ASCENDING), ('status', ASCENDING)],
                            background=True)
    phoneplani.ensure_index([('owner', ASCENDING), ('phonenumber', ASCENDING), ('is_delete', ASCENDING)],
                            background=True)
    phoneplani.ensure_index([('owner', ASCENDING), ('addplantime', DESCENDING),
                             ('sort_id', DESCENDING)], background=True)
    phoneplani.ensure_index([('sort_id', DESCENDING)], background=True)
    phoneplani.ensure_index([('owner', ASCENDING), ('sort_id', DESCENDING)], background=True)
    phoneplani.ensure_index([('owner', ASCENDING)], background=True)
    phoneplani.ensure_index([('uptime', ASCENDING)], background=True)
    phoneplani.ensure_index([('phonenumber', "hashed")], background=True)
    phoneplani.ensure_index([('aidef', ASCENDING)], background=True)
    phoneplani.ensure_index([('PhoneUserInfo.areacode', ASCENDING)], background=True)
    phoneplani.ensure_index([('PhoneUserInfo.phonetype', ASCENDING)], background=True)
    phoneplani.ensure_index([('PhoneUserInfo.cname', ASCENDING)], background=True)
    phoneplani.ensure_index([('addplantime', DESCENDING)], background=True)
    phoneplani.ensure_index([('sort_id', DESCENDING)], background=True)
    phoneplani.ensure_index([('eid', ASCENDING), ('phonenumber', ASCENDING),
                             ('is_delete', ASCENDING)], unique=True, background=True)

    calltimei = db['calltime']
    calltimei.ensure_index([('uid', ASCENDING), ('createtime', ASCENDING)], background=True)
    calltimei.ensure_index([('eid', ASCENDING), ('createtime', ASCENDING)], background=True)
    calltimei.ensure_index([('resid', "hashed")], background=True)
    calltimei.ensure_index([('resid', ASCENDING), ('iconid', ASCENDING)], background=True)

    callschedulei = db['callschedule']
    callschedulei.ensure_index([('uid', ASCENDING), ('uicon', ASCENDING), ('start', ASCENDING), ('end', ASCENDING)],
                               background=True)
    callschedulei.ensure_index([('state', ASCENDING), ('enable_start', ASCENDING)], background=True)
    callschedulei.ensure_index([('uid', ASCENDING), ('uicon', ASCENDING), ('state', ASCENDING)], background=True)
    callschedulei.ensure_index([('uid', ASCENDING), ('uicon', ASCENDING), ('state', ASCENDING), ('isable', ASCENDING)],
                               background=True)
    callschedulei.ensure_index([('uid', ASCENDING), ('uicon', ASCENDING)], background=True)

    api_authenticationi = db['api_authentication']
    api_authenticationi.ensure_index([('user', ASCENDING), ('password', ASCENDING)], background=True)

    phoneresinfoi = db['phoneresinfo']
    phoneresinfoi.ensure_index([('micon', "hashed")], background=True)
    phoneresinfoi.ensure_index([('planid', "hashed")], background=True)
    phoneresinfoi.ensure_index([('phonenumber', "hashed")], background=True)
    phoneresinfoi.ensure_index([('pid', ASCENDING)], background=True)
    phoneresinfoi.ensure_index([('phonenumber', ASCENDING), ('eid', ASCENDING), ('sed', ASCENDING)], background=True)
    phoneresinfoi.ensure_index([('uid', ASCENDING), ('phoneprocessinfo.restag', ASCENDING), ('lastime', DESCENDING),
                                ('restime', DESCENDING)], background=True)
    phoneresinfoi.ensure_index([('micon', ASCENDING), ('uid', ASCENDING), ('sed', ASCENDING), ('state', ASCENDING)],
                               background=True)
    phoneresinfoi.ensure_index([('micon', ASCENDING), ('lastime', ASCENDING)], background=True)
    phoneresinfoi.ensure_index([('planid', ASCENDING), ('isrunnig', ASCENDING)], background=True)

    recordfileinfoi = db['recordfileinfo']
    recordfileinfoi.ensure_index([('uid', ASCENDING), ("user", ASCENDING)], background=True)
    recordfileinfoi.ensure_index([('micon', ASCENDING)], background=True)
    recordfileinfoi.ensure_index([('time', ASCENDING)], background=True)
    recordfileinfoi.ensure_index([('eid', ASCENDING), ('uid', ASCENDING), ('duration', ASCENDING)], background=True)
    recordfileinfoi.ensure_index([('time', ASCENDING), ('file', ASCENDING), ('word', ASCENDING), ('user', ASCENDING)],
                                 background=True)

    sipserverinfoi = db['sipserverinfo']
    sipserverinfoi.ensure_index([('sipip', ASCENDING)], background=True)

    templatesi = db['templates']
    templatesi.ensure_index([('eid', ASCENDING), ('uploader', ASCENDING), ('templateurl', ASCENDING)], background=True)

    # show index info:
    for collection_name in db.collection_names():
        print
        "Collection: [{}]".format(collection_name)
        col = db[collection_name]
        print
        col.index_information()


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('alchemydumps', AlchemyDumpsCommand)

if __name__ == '__main__':
    manager.run()
