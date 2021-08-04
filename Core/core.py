import csv
import json
import requests
import random
import time

from Message.message import sendFriendMessage
from Config.settings import config
from Logger.logger import logger


def main():
    path = config.path()
    path += '/Core/info.csv'
    with open(path, encoding='utf-8') as info:
        reader = csv.reader(info)
        for stu in reader:
            debug = config.settings("Debug", "DEBUG")
            if not debug:
                randtime = random.randint(1 * 60, 10 * 60)
                logger.info("Waiting for {} Secends".format(randtime))
                time.sleep(randtime)
            else:
                time.sleep(5)
            if stu[0] != '学校代码':
                # 登录页面，提交学校代码和学号，用于获取cookie，直接get请求
                loginurl = f'https://fxgl.jx.edu.cn/{stu[0]}/public/homeQd?loginName={stu[1]}&loginType=0'
                # 签到页面，需要使用cookie登录，post一系列参数实现签到
                signinurl = f'https://fxgl.jx.edu.cn/{stu[0]}/studentQd/saveStu'
                # 请求头
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68'
                }
                # 使用session会话保持技术，可跨请求保留cookie
                session = requests.session()
                # 访问登陆界面，获取到用户的cookie，保持于session会话中
                session.get(loginurl, headers=headers)
                # 需要post的数据
                data = {
                    'province': stu[2],      # 省份
                    'city': stu[3],          # 市
                    'district': stu[4],      # 区/县
                    'street': stu[5],        # 具体地址
                    'xszt': 0,
                    'jkzk': 0,               # 健康状况 0:健康 1:异常
                    'jkzkxq': '',            # 异常原因
                    'sfgl': 1,               # 是否隔离 0:隔离 1:未隔离
                    'gldd': '',
                    'mqtw': 0,
                    'mqtwxq': '',
                    'zddlwz': stu[2]+stu[3]+stu[4],    # 省市区
                    'sddlwz': '',
                    'bprovince': stu[2],
                    'bcity': stu[3],
                    'bdistrict': stu[4],
                    'bstreet': stu[5],
                    'sprovince': stu[2],
                    'scity': stu[3],
                    'sdistrict': stu[4],
                    'lng': stu[6],          # 经度
                    'lat': stu[7],           # 纬度
                    'sfby': 1                  # 是否为毕业生 0:是 1:否
                }
                result = session.post(url=signinurl, data=data, headers=headers).text
                # 访问接口返回的数据是json字符串，使用loads方法转换为python字典
                statusCode = json.loads(result)['code']
                QQ = stu[8]
                # 根据状态码判断签到状态
                if statusCode == 1001:
                    sendFriendMessage("{}疫情打卡签到成功".format(stu[1]), QQ)
                elif statusCode == 1002:
                    sendFriendMessage("{}疫情打卡今日已签".format(stu[1]), QQ)
                else:
                    sendFriendMessage("{}疫情打卡签到状态异常，请手动打卡".format(stu[1]), QQ)
