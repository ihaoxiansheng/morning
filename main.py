from datetime import date, datetime, timedelta
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now() + timedelta(hours=8)  # 2022-08-28 10:34:16.474916
start_date = os.environ['START_DATE']  # "2022-06-08"
meet_date = os.environ['MEET_DATE']  # 04-05
city = os.environ['CITY']  # 天津
birthday = os.environ['BIRTHDAY']  # 12-22

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_ids = os.environ["USER_ID"].split("\n")
template_id = os.environ["TEMPLATE_ID"]


# 获取农历日期 八月初一
def get_lunar_calendar():
    date = today.strftime("%Y-%m-%d")
    url = "http://api.tianapi.com/lunar/index?key=d5edced4967c76fd11899dbe1b753d91&date=" + date
    lunar_calendar = requests.get(url).json()
    res3 = lunar_calendar['newslist'][0]
    print(res3['lubarmonth'] + res3['lunarday'])
    return res3['lubarmonth'], res3['lunarday']


# 获取穿衣建议
def get_tips():
    url = "http://api.tianapi.com/tianqi/index?key=f614561f2dfa18f8642431319a618843&city=" + city
    res = requests.get(url).json()
    print(res['newslist'][0])
    newslist = res['newslist'][0]
    return newslist['tips'], newslist['sunrise'], newslist['sunset']


# 获取微信access_token
def get_access_token():
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    access_token = get(post_url).json()['access_token']
    print(access_token)
    return access_token


# 获取星期几
def get_week_day():
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    week_day = week_list[datetime.date(today).weekday()]
    return week_day


# 获取天气
def get_weather():
    url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
    res = requests.get(url).json()
    weather = res['data']['list'][0]
    return weather['humidity'], weather['wind'], weather['airData'], weather['airQuality'], weather['date'], weather[
        'weather'], math.floor(weather['temp']), math.floor(weather['high']), math.floor(weather['low'])


# 获取相恋天数
def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days


# 获取遇见天数
def get_meet():
    meet = today - datetime.strptime(meet_date, "%Y-%m-%d")
    return meet.days


# 获取生日天数
def get_birthday():
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    return (next - today).days


# 获取彩虹屁
def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


# 获取随机颜色
def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
humidity, wind, airData, airQuality, da, wea, temperature, highest, lowest = get_weather()
tips, sunrise, sunset = get_tips()
lunarmonth, lunarday = get_lunar_calendar()
data = {"today_date": {"value": da, "color": get_random_color()},
        "date1": {'value': '今天是：'},
        "city1": {'value': '城市：'},
        "weather1": {"value": '天气：'},
        "humidity1": {"value": '湿度：'},
        "wind1": {"value": '风向风力：'},
        "airData_Quality": {"value": '空气质量：'},
        "temperature1": {'value': '当前温度：'},
        "lowest1": {'value': '最低气温：'},
        "highest1": {'value': '最高气温：'},
        "meet_days1": {'value': '我们遇见已经：'},
        "love_days1": {'value': '我们相恋已经：'},
        "birthday_left1": {"value": '距离你的生日还有：'},
        "tips1": {"value": '穿衣建议：'},
        "sunrise1": {"value": '日出时间：'},
        "sunset1": {"value": '日落时间：'},
        "date": {"value": today.strftime('%Y年%m月%d日'), "color": get_random_color()},
        "week": {"value": get_week_day(), "color": get_random_color()},
        "weather": {"value": wea, "color": get_random_color()},
        "humidity": {"value": humidity, "color": get_random_color()},  # 湿度
        "wind": {"value": wind, "color": get_random_color()},  # 风向级
        "airData": {"value": airData, "color": get_random_color()},  # 空气指数
        "airQuality": {"value": airQuality, "color": get_random_color()},  # 空气质量
        "temperature": {"value": temperature, "color": get_random_color()},
        "love_days": {"value": get_count(), "color": get_random_color()},
        "birthday_left": {"value": get_birthday(), "color": get_random_color()},
        "city": {"value": city, "color": get_random_color()},
        "meet_days": {"value": get_meet(), "color": get_random_color()},
        "words": {"value": get_words(), "color": get_random_color()},
        "highest": {"value": highest, "color": get_random_color()},
        "tips": {"value": tips, "color": get_random_color()},
        "sunrise": {"value": sunrise, "color": get_random_color()},
        "sunset": {"value": sunset, "color": get_random_color()},
        "lunar_calendar": {"value": '农历' + lunarmonth + lunarday, "color": get_random_color()},
        "lowest": {"value": lowest, "color": get_random_color()}}
count = 0
for user_id in user_ids:
    res = wm.send_template(user_id, template_id, data)
    count += 1

print("发送了" + str(count) + "条消息")
