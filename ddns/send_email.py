# coding:utf-8
import smtplib
from email.mime.text import MIMEText


# 要发给谁
mailto_list = ["caizhihua@lsrobot.vip"]

# 设置服务器，用户名、口令以及邮箱的后缀
mail_host = "smtp.163.com"
mail_user = "huazhicai110@163.com"
mail_passwd = "huazhicai110"
mail_postfix = "163.com"

flag = True


# 发送邮件
def send_mail(sub, content, to_list=mailto_list):
    me = mail_user + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEText(content, 'html', 'utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ",".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_passwd)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(str(e))
        return False