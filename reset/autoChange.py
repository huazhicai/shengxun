#!/usr/bin/env python
# coding: utf-8
# Seven
import paramiko


class AutoModify(object):
    """
    重置密码
    添加修改aim_sn
    获取用户id
    取消计划中的号码已取
    创建用户（开号）
    恢复删除的数据
    """

    def __init__(self, url, path, port=22):
        private_key = paramiko.RSAKey.from_private_key_file('/home/blj/.ssh/id_rsa')
        # 创建SSH对象
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接服务器
        self.ssh.connect(hostname=url, port=port, username='root', pkey=private_key)
        self.command = 'cd {} && docker-compose exec -T telemarket-old python manage.py'.format(path)

    def do_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        res_out = stdout.read()
        print(res_out)
        res_err = stderr.read()
        print(res_err)

    def modify_password(self):
        name = raw_input('Username: ')
        new_password = raw_input('New password: ').strip()
        expre = """ shell<<EOF
user = User.query.filter_by(username='{0}').first()
autocommit=True
user.password='{1}'
db.session.add(user)
db.session.commit()EOF
""".format(name, new_password)
        command = self.command + expre
        print(command)
        self.do_command(command)

    def add_sn(self):
        name = raw_input('Username: ')
        aim_sn = raw_input('aim_sn: ').strip()
        expre = """ shell<<EOF
user = User.query.filter_by(username='{0}').first()
user.aim_sn='{1}'
db.session.add(user)
db.session.commit()
EOF
""".format(name, aim_sn)
        command = self.command + expre
        print(command)
        self.do_command(command)

    def cancel_plan(self):
        user_id = raw_input('User id: ')
        expre = """ shell<<EOF
phoneplan.objects(owner={}, isdial=0).update(set__isdial=0)
EOF
""".format(user_id)
        command = self.command + expre
        self.do_command(command)

    def get_user_id(self):
        name = raw_input('Username: ')
        command = self.command + ' getuserid ' + name
        self.do_command(command)

    def create_user(self):
        username = raw_input('Username: ')
        password = raw_input('Password: ')
        email = raw_input('Email: ')
        inc_name = raw_input('Inc_name: ')
        phone = raw_input('Mobile phone: ')
        ai_num = raw_input('Ai number: ')
        aim_sn = raw_input('aim_sn: ')
        command = self.command + ' create_e_user -u {0} -p {1} -e {2} -i {3} -m {4} -n {5} -o {6}'.format(
                username, password, email, inc_name, phone, ai_num, aim_sn
        )
        print(command)
        try:
            self.do_command(command)
            print('****** {} has been created!!! ******'.format(username))
        except Exception as err:
            print(err)

    def restore_deleted(self):
        user_id = raw_input('User id: ')
        command = self.command + ' restore_deleted ' + user_id
        self.do_command(command)

    def show_menu(self):
        prompt = """
        (m)odify password
        (a)dd aim_sn
        (g)et user id
        (c)reate user
        (r)estore deleted
        (p)plan cancellation
        (q)uit

        Enter choice: """

        done = False
        while not done:
            chosen = False
            while not chosen:
                try:
                    choice = raw_input(prompt)[0]
                except (EOFError, KeyboardInterrupt, IndexError) as err:
                    print(err)
                    choice = 'q'
                print('\nYou picked: [%s]' % choice)

                if choice not in 'magcrpq':
                    print('invalid menu option, try again')
                else:
                    chosen = True

            if choice == 'q':
                done = True
                self.ssh.close()
            if choice == 'm': self.modify_password()
            if choice == 'a': self.add_sn()
            if choice == 'p': self.cancel_plan()
            if choice == 'g': self.get_user_id()
            if choice == 'c': self.create_user()
            if choice == 'r': self.restore_deleted()


def main():
    prompt = """
        (a)listenrobot.com
        (b)lingsheng.ai
        (c)listenrobot.cn
        (q)uit

        Enter choice: """

    done = False
    while not done:
        chosen = False
        while not chosen:
            try:
                choice = raw_input(prompt)[0]
            except (EOFError, KeyboardInterrupt, IndexError) as err:
                print(err)
                choice = 'q'
            print('\nYou picked: [%s]' % choice)

            if choice not in 'abcq':
                print('invalid menu option, try again')
            else:
                chosen = True

        if choice == 'a':
            url = 'console.listenrobot.com'
            path = '/datahome/old-telemarket-deploy/'
            auto = AutoModify(url, path)
            auto.show_menu()
        elif choice == 'b':
            url = 'console.lingsheng.ai'
            path = '/data/old-telemarket-deploy'
            auto = AutoModify(url, path)
            auto.show_menu()
        elif choice == 'c':
            url = raw_input('hostname: ')
            port = input('port(10022 or 10023: ')
            path = raw_input('/root/old-telemarket-deploy/ or /home/old-telemarket-deploy/\n:')
            auto = AutoModify(url, path, port=port)
            auto.show_menu()
        elif choice == 'q':
            done = True


if __name__ == '__main__':
    main()
