import datetime, time
from config import LIMIT_NEXT_DIAL_TIME
from app.foundation import log, db
from app.common.constants import MobileStatus, DailResult, MobileRegion
from app.cache.mobile_count_cache import mobile_count_cache
from app.logic.mobile_query_logic import get_conditions
from app.logic.sub_table_logic import get_mobile_model, get_dialtask_model
from app.common.constants import MobileStatus
from app.common.db_helper import count_where
from utility.tool import get_cur_ts


def del_count_cache(user_id):
    mobile_count_cache.delete(user_id, MobileRegion.PRIVATE)
    mobile_count_cache.delete(user_id, MobileRegion.PUBLIC)


def get_contacting_mobile_count(user_id):
    start_time = get_cur_ts() - (7 * 24 * 60 * 60)
    end_time = get_cur_ts()
    Mobile = get_mobile_model(user_id)
    conditions = get_conditions(Mobile, [user_id], start_time, end_time, status=MobileStatus.MOBILE_CONTACTING)
    contacting_mobile_count = count_where(*conditions)
    return contacting_mobile_count


def restore_deleted(user_id, date_str):
    Mobile = get_mobile_model(user_id)
    date_ts = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    date_ts = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    date_end = date_ts + datetime.timedelta(hours=24)
    DialTask = get_dialtask_model(user_id)
    del_mobiles = Mobile.query.filter(Mobile.is_delete == True,
                                      Mobile.user_id == user_id,
                                      Mobile.update_time > date_ts,
                                      Mobile.update_time < date_end).all()

    for del_mobile in del_mobiles:
        try:
            del_mobile.is_delete = False
            dialtasks = DialTask.query.filter(DialTask.mobile_id == del_mobile.id,
                                              DialTask.is_delete == True,
                                              DialTask.update_time > date_ts,
                                              DialTask.update_time < date_end).all()
            for dialtask in dialtasks:
                dialtask.is_delete = False
            db.session.commit()
        except Exception as e:
            log.exception(e)
            db.session.rollback()

python3 manage.py restore_deleted_mobile 109 2018-05-23
