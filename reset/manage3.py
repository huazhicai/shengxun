# coding=utf-8

from flask_script import Server, Shell, Manager, prompt_bool

from app.foundation import db, redis, log
from app.models.User import User
from app.models.UserGroup import UserGroup
from app.models.RoleConfig import RoleConfig
from app.models.ImportTask import ImportTask
from app.models.AuthPermiss import AuthPermiss
from app.models.ResultSum import ResultSum
from app.common.constants import UserRole
from app.models.DialTaskEx import DialTaskModels
from app.models.MobileEx import MobileModels
from sqlalchemy import text
from flask_migrate import Migrate, MigrateCommand
from app import views
from app import app
from config import SECRET_KEY
from flask_alchemydumps import AlchemyDumpsCommand
from sqlalchemy import func, Index
import datetime
from app.models.DialTaskEx import DialTaskEx
from app.common.constants import DailDuringType
from app.logic.sum_logic import classified_statistic

try:
    from config import DEFAULT_COMPANY_NAME
except ImportError:
    DEFAULT_COMPANY_NAME = u'声讯'

# app = create_app()
app.debug = True
app.secret_key = SECRET_KEY
manager = Manager(app)

manager.add_command("runserver", Server('0.0.0.0', port=8200))


def _make_context():
    return dict(db=db)


manager.add_command("shell", Shell(make_context=_make_context))


@manager.command
def resetpwd(user_name, new_password):
    reset_user = User.query.filter(User.username == user_name, User.is_delete == False).first()
    reset_user.update(password=new_password)
    db.session.commit()


def init_role():
    for res in views.MODULES:
        db.session.add(
                RoleConfig(
                        role=UserRole.ROLE_ROOT, resource=res.name,
                        can_create=True, can_read=True, can_update=True, can_delete=True
                )
        )
        db.session.add(
                RoleConfig(
                        role=UserRole.ROLE_ADMIN, resource=res.name,
                        can_create=True, can_read=True, can_update=True, can_delete=True
                )
        )
        db.session.add(
                RoleConfig(
                        role=UserRole.ROLE_NORMAL, resource=res.name,
                        can_create=True, can_read=True, can_update=True, can_delete=True
                )
        )
        db.session.add(
                RoleConfig(
                        role=UserRole.ROLE_CUSTOMER, resource=res.name,
                        can_create=True, can_read=True, can_update=True, can_delete=True
                )
        )
    db.session.commit()


def init_user_group():
    # db.session.add(UserGroup(id=1, name="市局", parent_id=0))
    db.session.commit()


@manager.command
def fix_call_task():
    from app.logic.call_task_logic import fix_invalid_dail_task
    users = User.query.all()
    for user in users:
        fix_invalid_dail_task(user.id)
    db.session.commit()


def add_user(role, name, password=None, user_group_id=1):
    if not password:
        password = name
    user = User(username=name, real_name=name, password=password, role=role, group_id=user_group_id)
    db.session.add(user)
    db.session.flush()
    UserGroup.query.filter(UserGroup.id == user.group_id).update({'leader_id': user.id, 'leader_name': user.name},
                                                                 synchronize_session=False)
    db.session.commit()


def add_test_user(count):
    for i in range(1, count):
        user = User(username='user' + str(i), real_name='user' + str(i), password='user' + str(i),
                    role=UserRole.ROLE_NORMAL)
        db.session.add(user)
    db.session.commit()


def add_grant(count):
    # roleConfig = RoleConfig(role=3,resource='frontend',can_create=True,can_read=True,can_update=True,can_delete=True)
    # db.session.add(roleConfig)
    db.session.commit()


def mock_data():
    db.session.commit()


def _creat_index():
    pass


@manager.command
def restore_deleted_mobile(user_id, date_str):
    from app.logic.mobile_logic import restore_deleted
    restore_deleted(user_id, date_str)


@manager.command
def createall():
    db.create_all()
    _creat_index()
    db.session.commit()
    AuthPermiss.create_users()
    init_user_group()
    init_role()
    group_root = UserGroup(name='root')
    group_admin = UserGroup(name=DEFAULT_COMPANY_NAME)
    group_user = UserGroup(name='user')
    group_customer = UserGroup(name='customer')
    db.session.add(group_root)
    db.session.add(group_admin)
    db.session.add(group_user)
    db.session.add(group_customer)

    db.session.flush()
    group_root.company_id = group_root.id
    group_admin.company_id = group_admin.id
    group_user.company_id = group_user.id
    add_user(UserRole.ROLE_ADMIN, 'admin', 'sx-tech1@#&111', group_admin.id)
    add_user(UserRole.ROLE_CUSTOMER, 'customer', 'customer', group_customer.id)
    mock_data()


@manager.command
def create_index():
    _creat_index()


@manager.command
def switch_aimsn(old_aim_sn, new_aim_sn):
    old_users = User.query.filter(User.aim_sn == old_aim_sn).all()
    for old_user in old_users:
        if prompt_bool("Are you sure ? switch user: " + old_user.aim_sn):
            old_user.aim_sn = new_aim_sn
    db.session.commit()


@manager.command
def dropall(pass_ask=None):
    "Drops all database tables"
    if pass_ask:
        db.drop_all()
    else:
        if prompt_bool("Are you sure ? You will lose all your data !"):
            db.drop_all()


def clear_redis():
    redis.db.flushall()


# @manager.command
# def resetall(pass_ask=None):
#     dropall(pass_ask)
#     clear_redis()
#     createall()

@manager.command
def delete_alembic():
    sql = text('DROP TABLE alembic_version;')
    db.engine.execute(sql)


@manager.command
def recover_dialtime(recover_startime, recover_endtime):
    recover_startdate = datetime.datetime.fromtimestamp(recover_startime)
    recover_endate = datetime.datetime.fromtimestamp(recover_endtime)
    from app.logic.sub_table_logic import get_dialtask_model
    user_list = User.query.filter(User.is_delete == False).all()
    dt = (recover_startdate + datetime.timedelta(days=1)).date()
    log.info('dt_manage_: ' + str(dt))
    log.info('recover_startdate: ' + str(recover_startdate))
    log.info('recover_endate: ' + str(recover_endate))
    for user in user_list:
        res, dialtime_5, dialtime_10, dialtime_30, dialtime_sum = classified_statistic(user, recover_startdate,
                                                                                       recover_endate)
        log.info('user_id: ' + str(user.id) + ' res: ' + str(res))
        for callphone, label_ in res.items():
            for label, code_ in res[callphone].items():
                for code, total_count in res[callphone][label].items():
                    code_sum = ResultSum.query.filter(ResultSum.sum_date == dt, ResultSum.user_id == user.id,
                                                      ResultSum.callphone == callphone, ResultSum.tag == label,
                                                      ResultSum.code == code).first()
                    if code_sum:
                        code_sum.number = total_count
                    else:
                        new_code_sum = ResultSum(sum_date=dt, user_id=user.id, callphone=callphone,
                                                 tag=label, code=code, number=total_count)
                        db.session.add(new_code_sum)
        during_type_5 = ResultSum.query.filter(ResultSum.user_id == user.id,
                                               ResultSum.dail_during_type == DailDuringType.DAILDURING_BIG5,
                                               ResultSum.sum_date == dt).first()
        if not during_type_5:
            new_during_type_5 = ResultSum(sum_date=dt, user_id=user.id, dail_during_type=DailDuringType.DAILDURING_BIG5,
                                          number=dialtime_5)
            db.session.add(new_during_type_5)
        else:
            during_type_5.number = dialtime_5
        during_type_10 = ResultSum.query.filter(ResultSum.user_id == user.id,
                                                ResultSum.dail_during_type == DailDuringType.DAILDURING_BIG10,
                                                ResultSum.sum_date == dt).first()
        if not during_type_10:
            new_during_type_10 = ResultSum(sum_date=dt, user_id=user.id,
                                           dail_during_type=DailDuringType.DAILDURING_BIG10, number=dialtime_10)
            db.session.add(new_during_type_10)
        else:
            during_type_10.number = dialtime_10
        during_type_30 = ResultSum.query.filter(ResultSum.user_id == user.id,
                                                ResultSum.dail_during_type == DailDuringType.DAILDURING_BIG30,
                                                ResultSum.sum_date == dt).first()
        if not during_type_30:
            new_during_type_30 = ResultSum(sum_date=dt, user_id=user.id,
                                           dail_during_type=DailDuringType.DAILDURING_BIG30, number=dialtime_30)
            db.session.add(new_during_type_30)
        else:
            during_type_30.number = dialtime_30
        dial__time_sum = ResultSum.query.filter(ResultSum.sum_date == dt, ResultSum.user_id == user.id,
                                                ResultSum.dial_time_sum != None).first()
        if not dial__time_sum:
            new_dialtime_sum = ResultSum(sum_date=dt, user_id=user.id, dial_time_sum=dialtime_sum)
            db.session.add(new_dialtime_sum)
        else:
            dial__time_sum.dial_time_sum = dialtime_sum
        log.info('user_id: ' + str(user.id) + ' dialtime_sum: ' + str(dialtime_sum))
        db.session.commit()


migrate = Migrate(app, db)

# migrate = Migrate(app, db, directory="/")
manager.add_command('alchemydumps', AlchemyDumpsCommand)
manager.add_command('db', MigrateCommand)
if __name__ == "__main__":
    manager.run()
