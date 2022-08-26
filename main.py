from datetime import date, datetime, timedelta
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
import http.client, urllib

today = datetime.now() + timedelta(hours=8)
start_date = os.environ['START_DATE']
meet_date = os.environ['MEET_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_ids = os.environ["USER_ID"].split("\n")
template_id = os.environ["TEMPLATE_ID"]

conn = http.client.HTTPSConnection('api.tianapi.com')  # 接口域名
params = urllib.parse.urlencode({'key':'f614561f2dfa18f8642431319a618843','city':'天津市'})
headers = {'Content-type':'application/x-www-form-urlencoded'}
conn.request('POST','/tianqi/index',params,headers)
res = conn.getresponse()
data = res.json
print("========================" + data.decode('utf-8'))
print("11111111111111111111")
returnValue = data.decode('utf-8')
newslist = returnValue['newslist'][0]
print(newslist)
print(newslist['tips'])

def get_access_token():
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    access_token = get(post_url).json()['access_token']
    print(access_token)
    return access_token

def get_week_day(date):
    week_day = {
        0: '星期一',
        1: '星期二',
        2: '星期三',
        3: '星期四',
        4: '星期五',
        5: '星期六',
        6: '星期日',
    }
    day = date.weekday()  # weekday()可以获得是星期几
    return week_day[day]

def get_weather():
  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  res = requests.get(url).json()
  weather = res['data']['list'][0]
  print(weather['humidity'])
  print(weather['wind'])
  print(weather['airData'])
  print(weather['airQuality'])
  for group in weather:
    print("group==========" + group)
  return weather['humidity'], weather['wind'], weather['airData'], weather['airQuality'], weather['date'], weather['weather'], math.floor(weather['temp']), math.floor(weather['high']), math.floor(weather['low'])

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_meet():
  meet = today - datetime.strptime(meet_date, "%Y-%m-%d")
  return meet.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
humidity, wind, airData, airQuality, da, wea, temperature, highest, lowest = get_weather()
data = {"today_date":{"value":da,"color":get_random_color()}, # xxxx-xx-xx
        "date1":{'value':'📅今天是：'},
        "city1":{'value':'🏙城市：'},
        "weather1":{"value":'🌤天气：'},
        "humidity1":{"value":'💧湿度：'},
        "wind1":{"value":'🌪风向风力：'},
        "airData_Quality":{"value":'🌲空气质量：'},
        "temperature1":{'value':'🌡当前温度：'},
        "lowest1":{'value':'🍃最低气温：'},
        "highest1":{'value':'🔥最高气温：'},
        "meet_days1":{'value':'🎵我们遇见已经：'},
        "love_days1":{'value':'💕我们相恋已经：'},
        "birthday_left1":{"value":'🎂距离你的生日还有：'},
        "date":{"value":today.strftime('%Y年%m月%d日'),"color":get_random_color()},
        "week":{"value":get_week_day(datetime.now()),"color":get_random_color()},
        "weather":{"value":wea,"color":get_random_color()},
        "humidity":{"value":humidity,"color":get_random_color()}, # 湿度
        "wind":{"value":wind,"color":get_random_color()}, # 风向级
        "airData":{"value":airData,"color":get_random_color()}, # 空气指数
        "airQuality":{"value":airQuality,"color":get_random_color()}, # 空气质量
        "temperature":{"value":temperature,"color":get_random_color()},
        "love_days":{"value":get_count(),"color":get_random_color()},
        "birthday_left":{"value":get_birthday(),"color":get_random_color()},
        "city":{"value":city,"color":get_random_color()},
        "meet_days":{"value":get_meet(),"color":get_random_color()},
        "words":{"value":get_words(),"color":get_random_color()},
        "highest": {"value":highest,"color":get_random_color()},
        "lowest":{"value":lowest, "color":get_random_color()}}
count = 0
for user_id in user_ids:
  res = wm.send_template(user_id, template_id, data)
  count+=1

print("发送了" + str(count) + "条消息")
