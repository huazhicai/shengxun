import sys

username = sys.argv[1]
password = sys.argv[2]


def reset_password(username, password):
    current_user = db.session.query(User).filter_by(username=username).first()
    current_user.password = password
    db.session.add(current_user)
    db.session.commit()
    return 'password has been changed!'


reset_password(username, password)
