import os
import re
import sys
import uuid
import time
import datetime
import json
import socket
import requests
import traceback
from inspect import getframeinfo, stack

sys.path.append("..")
from util.logger import Logger
from util.config import LoadConfig

logger = Logger(os.path.basename(__file__))


def gen_uuid():
    """ 生成UUID """
    uid = uuid.uuid1()
    return uid.hex


def get_cur_timestamp():
    """ 获取当前时间戳 """
    return int(time.time())


def get_cur_timestr(time_foramt='%Y-%m-%d %H:%M:%S'):
    """ 获取当前时间字符串 """
    return timestamp2timestr(get_cur_timestamp(), time_foramt)


def timestamp2timestr(timestamp, time_format='%Y-%m-%d %H:%M:%S', offset_z=0):
    """
    :param timestamp: 时间戳
    :param time_format:
    :param offset_z: 时区差, 东加西减
    :return: 时间字符串
    """
    return time.strftime(time_format, time.localtime(timestamp + offset_z * 3600))


def timestr2timestamp(time_string, time_foramt='%Y-%m-%d %H:%M:%S', offset_z=0):
    """
    :param time_string:时间字符串
    :param time_foramt:
    :param offset_z: 时区差, 东加西减
    :return: 时间戳
    """
    return int(time.mktime(datetime.datetime.strptime(time_string, time_foramt).timetuple())) + offset_z * 3600


def convert_time_format(input_time_str, from_format='%Y-%m-%d_%H:%M:%S', to_format='%Y-%m-%d %H:%M:%S'):
    """ 转换时间格式 """
    timestamp = timestr2timestamp(input_time_str, from_format)
    res_time_str = timestamp2timestr(timestamp, to_format)
    return res_time_str


def get_cur_utc_timestamp():
    """ 获取当前utc时间戳 """
    utc_timestamp = datetime.datetime.utcnow().timestamp()
    return int(utc_timestamp)


def get_cur_utc_str(utc_time_string_foramt='%Y-%m-%dT%H:%M:%SZ'):
    """ 获取当前时间字符串 """
    return timestamp2timestr(get_cur_utc_timestamp(), utc_time_string_foramt)


def utc2local(utc_timestamp):
    """ UTC 时间戳 => 本地时间戳 """
    local_tm = datetime.datetime.fromtimestamp(0)
    utc_tm = datetime.datetime.utcfromtimestamp(0)
    offset = local_tm - utc_tm
    return utc_timestamp + offset.seconds


def local2utc(local_timestamp):
    """ 本地时间戳 => UTC 时间戳 """
    utc_timestamp = datetime.datetime.utcfromtimestamp(local_timestamp).timestamp()
    return int(utc_timestamp)


def get_host_ip():
    """ 获取当前设备 ip 地址 """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def send2dingtalk(text, key_word='[Monitor]', access_token='b745791966ee2d75a93e4b2ba5991bddad9945daadd0c7a51b65c747d5c60798', at=None):
    """ 发送消息到钉钉 """
    caller = getframeinfo(stack()[1][0])
    filename = ""
    if '/' in caller.filename:
        filename = caller.filename.split('/')[-1]
    else:
        filename = caller.filename.split('\\')[-1]

    msg = f"### 服务出现异常，请及时关注 \n" \
          f"##### file: {filename}:{caller.lineno} \n" \
          f"##### time: {get_cur_timestr()} \n" \
          f"##### {text} \n" \
          f"##### track:{traceback.format_exc()}"

    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    url = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}'
    data = {
        "msgtype":  "markdown",
        "markdown": {
            "title": key_word,
            "text":  msg
        }
    }
    if at is not None:
        data['at'] = {'atMobiles': [at]}
        data['markdown']['text'] = msg + "\n### @" + '\n'.join(at) + ' \n'

    logger.info(f'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {url}\nrequest:{json.dumps(data)}')
    res = requests.post(url, headers=headers, data=json.dumps(data))
    logger.info(f'<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< {url}\nresponse:{res.text}')


def remove_punct(text):
    """
    正则去掉字符串中所有的标点符号
    :param text: 带标点的字符串
    :return: 不带标点的字符串
    """
    punc = '~`!#$%^&*()_+-=|\';"＂:/.,?><~·！@#￥%……&*（）——+-=“：’；、。，？》{《}】【\n\]\['
    res_str = re.sub(r"[%s]+" % punc, "", text)
    return res_str


def format_address(contract):
    """ 格式化合约地址 """
    if not contract.startswith('0x'):
        contract = f"0x{contract}"
    return str(contract).lower()


def filter_emoji(desstr, restr=''):
    """ 过滤表情 """
    if desstr is None or desstr == 'None':
        return ''
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, desstr)


if __name__ == "__main__":
    # udid_str = gen_uuid()
    # logger.info(f"generate udid: {udid_str}\n\n")

    # ********************************* utc time *********************************
    # cur_utc_str = get_cur_utc_str()
    # cur_utc_timestamp = get_cur_utc_timestamp()
    # convert_utc_timestamp = timestr2timestamp(cur_utc_str, '%Y-%m-%dT%H:%M:%SZ')
    # convert_utc_str = timestamp2timestr(cur_utc_timestamp, '%Y-%m-%dT%H:%M:%SZ')
    # logger.info(f"utc str:                      {cur_utc_str}")
    # logger.info(f"utc timestamp:                {cur_utc_timestamp}")
    # logger.info(f"utc str to utc timestamp:     {convert_utc_timestamp}")
    # logger.info(f"utc timestamp to utc timestr: {convert_utc_str}\n")

    # ********************************* local time *********************************
    # cur_time_str = get_cur_timestr()
    # cur_timestamp = get_cur_timestamp()
    # convert_timestamp = timestr2timestamp(cur_time_str)
    # convert_time_str = timestamp2timestr(cur_timestamp)
    # logger.info(f"local timestr:                    {cur_time_str}")
    # logger.info(f"local timestamp:                  {cur_timestamp}")
    # logger.info(f"local str to local timestamp:     {convert_timestamp}")
    # logger.info(f"local timestamp to local timestr: {convert_time_str}\n")

    # ********************************* utc local 时间戳转换 *********************************
    # local_timestamp = utc2local(cur_utc_timestamp)
    # utc_timestamp = local2utc(cur_timestamp)
    # logger.info(f"utc_timestamp to local_timestamp:\t{local_timestamp}")
    # logger.info(f"local_timestamp to utc_timestamp:\t{utc_timestamp}\n")

    # ********************************* 连续时间字符串转通用时间字符串 *********************************
    # from_time_str = '2022-07-30_00:00:00'
    # res_time_str = convert_time_format(from_time_str)
    # logger.info(f"from time str:\t{from_time_str}")
    # logger.info(f"to time str:  \t{res_time_str}\n\n")

    # send2dingtalk('测试', access_token='b745791966ee2d75a93e4b2ba5991bddad9945daadd0c7a51b65c747d5c60798')

    # ts = set()
    # ts.add(3)
    # logger.info(f"\nset value:\t{ts} \n3 in ts:\t{3 in ts}")

    # td = {}
    # td['key1'] = 1
    # td['key2'] = 2
    # td['key3'] = 3
    # for key in td:
    #     logger.info(f"dictionary key:{key} value:{td[key]}")

    # str_with_punct = "hello,world!"
    # res_str = remove_punct(str_with_punct)
    # logger.info(f"\norigin text:    \t{str_with_punct} \nremove punctuation:\t{res_str}")

    content = '👍, very good!'
    logger.info(filter_emoji(content))
