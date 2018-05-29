from flask_script import Manager, Shell, prompt_bool
import time
import json


# 把联系中的ABCD类移回到已联系中
phoneplan = '123456'

def reset_getnumbered(userid):
    ABCD = ["A", "B", "C", "D" "E", "F"]
    is_dial = [1]
    current_time = int(time.time())
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


def getuserid(username):
    likename = "%" + username + "%"
    users = db.session.query(User).filter(User.username.like(likename)).all()
    for user in users:
        print("%d : %s" % (user.id, user.username))
