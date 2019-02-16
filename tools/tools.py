import hashlib
import binascii
from flask_mail import Message
''
reset1 = '<table border="0" cellpadding="0" cellspacing="0" width="100%"><tbody><tr><td bgcolor="#f7f9fa" align="center" style="padding:22px 0 20px 0"><table border="0" cellpadding="0" cellspacing="0" style="background-color:f7f9fa; border-radius:3px;border:1px solid #dedede;margin:0 auto; background-color:#ffffff" width="552"><tbody><tr><td bgcolor="#ffffff" align="center" style="padding: 0 15px 0px 15px;"><table border="0" cellpadding="0" cellspacing="0" width="480"><tbody><tr><td><table width="100%" border="0" cellpadding="0" cellspacing="0"><tbody><tr><td><table cellpadding="0" cellspacing="0" border="0" align="left"><tbody><tr><td width="550" align="left" valign="top"><table width="100%" border="0" cellpadding="0" cellspacing="0"><tbody><tr><td bgcolor="#ffffff" align="left" style="background-color:#ffffff; font-size: 17px; color:#7b7b7b; padding:28px 0 0 0;line-height:25px;"><b>亲爱的用户，你好!您的验证码为:<b style="background-color:#ffffff;color:red">'
reset2 = '</b></b></td></tr><tr><td bgcolor="#ffffff" align="left" style="background-color:#ffffff; font-size: 17px; color:#7b7b7b; padding:28px 0 0 0;line-height:25px;"></td></tr><tr><td align="left" valign="top" style="font-size:15px; color:#7b7b7b; font-size:14px; line-height: 25px; font-family:Hiragino Sans GB; padding: 20px 0px 20px 0px">我们已经收到了你的密码修改请求，请 24 小时内点击下面的按钮修改密码。</td></tr><tr><td style="border-bottom:1px #f1f4f6 solid; padding: 10px 0 35px 0;" align="center"><table border="0" cellspacing="0" cellpadding="0"><tbody><tr><td><span style="font-family:Hiragino Sans GB;font-size:17px;"><a style="text-decoration:none;color:#ffffff;" href="http://127.0.0.1:8080/reset" target="_blank" rel="noopener"><div style="padding:10px 25px 10px 25px;border-radius:3px;text-align:center;text-decoration:none;background-color:#ffa800;color:#ffffff;font-size:17px;margin:0;white-space:nowrap">修改密码</div></a></span></td></tr></tbody></table></td></tr><tr><td align="left" valign="top" style="font-size:15px; color:#7b7b7b; font-size:14px; line-height: 25px; font-family:Hiragino Sans GB; padding: 20px 0px 35px 0px">如果以上按钮无法打开，请把下面的链接复制到浏览器地址栏中打开：<a href="http://127.0.0.1:8080/reset" target="_blank" rel="noopener">http://127.0.0.1:8080/reset</a></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table>'
def encryption(password, salt):
    """
    密码加密通用方法
    :param password:密码 二进制
    :param salt: salt 二进制
    :return:
    """
    hash_lib1 = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 2)
    hash_password = binascii.hexlify(hash_lib1).decode('utf-8')
    return hash_password


def send_mail(mail, mail_number, title, text):
    """
    邮件发送的通用方法
    :param mail:
    :param mail_number:
    :param title:
    :param text:
    :return:
    """
    msg = Message(title,
                  recipients=[mail_number])
    msg.html = text
    mail.send(msg)
