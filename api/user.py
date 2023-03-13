import time
import random
import threading
import time

from operation.user import User_opration
from utils.data_process import Class_To_Data
from utils.debug import DEBUG
from error_code import *
from utils.verify_code import send_code

VERIFY_CODE_INTERVAL = 3600
# 用于存储验证码的dict
# 格式是 {"18312341234" : {"code":1234, "time":1668931308.123456}}
verify_code_dict = {}
t1 = None
def create_timer():
    DEBUG(func='create_timer')    
    for data in verify_code_dict:
        DEBUG(data=data)
        if ((verify_code_dict[data]['time']) - time.time()) > VERIFY_CODE_INTERVAL:
            verify_code_dict.pop(data)
    global t1
    t1 = threading.Timer(VERIFY_CODE_INTERVAL+VERIFY_CODE_INTERVAL/2, create_timer)
    t1.start()

def User_list():
    DEBUG(func='api/User_list')
    u_o = User_opration()
    data = u_o._all()
    # data（复杂对象）====> 数据
    data = Class_To_Data(data, u_o.__fields__, 0)
    DEBUG(data=data)
    return data

# def User_reg(kwargs):
#     u_o = User_operation()
#     data = u_o._reg(kwargs)
#     return data

def User_login(loginType,account,pwd):
    u_o = User_opration()
    # 手机号，验证码登录
    DEBUG(func='api/User_login')
    if loginType == 0:
        if account not in verify_code_dict or pwd != verify_code_dict[account]['code']:
            return USER_VERIFY_CODE_ERROR
        elif (time.time() - verify_code_dict[account]['time']) > 3600:
            verify_code_dict.pop(account)
            return USER_VERIFY_CODE_EXPIRED
        else:
            verify_code_dict.pop(account)
            return OK
    
    # 手机号/邮箱，密码登录
    data = u_o._login(loginType,account,pwd)
    if data is None:
        return USER_ACCOUNT_NONEXISTS
    data = Class_To_Data(data,u_o.__fields__, 1)
    if len(data) == 0:
        return USER_ACCOUNT_NONEXISTS
    if pwd != data['password']:
        return USER_PASSWORD_ERROR
    
    return OK

def User_send_verify_code(phone):
    DEBUG(func='api/User_send_verify_code')
    global t1
    if not t1:
        t1 = threading.Timer(5, create_timer)
        t1.start()

    code = ""
    for _ in range(6):
        code += str(random.randint(0,9))
    ans = send_code(code)
    if ans == OK:
        verify_code_dict[phone] = {}
        verify_code_dict[phone]['code'] = code
        verify_code_dict[phone]['time'] = time.time()
        # if DEBUG: print('send_verify_code:{}'.format(verify_code_dict))
        DEBUG(verify_code_dict=verify_code_dict)
    
    return ans

def User_verify_verify_code(phone, verify_code):
    DEBUG(func='api/User_verify_verify_code')
    if phone not in verify_code_dict or verify_code != verify_code_dict[phone]['code']:
        return USER_VERIFY_CODE_ERROR
    elif (time.time() - verify_code_dict[phone]['time']) > 3600:
        verify_code_dict.pop(phone)
        return USER_VERIFY_CODE_EXPIRED
    else:
        verify_code_dict.pop(phone)
        return OK