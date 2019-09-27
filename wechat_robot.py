# -*- coding: utf-8 -*-

# 导入模块
from wxpy import *
import requests
import json
import random

#茉莉API地址：http://i.itpk.cn/api.php
#图灵API地址：http://www.tuling123.com/openapi/api
TULIN_TOKEN = '5da047a95db8450ea6e710dd065d4be4' #'4cb9814aa00b41d38a1c0abc5a00c929' #0d26f7c76ecf4623a536368eaf3d26ea
MOLI_TOKEN = "ac00db995a4a8f2a3f3623c82f3cc9d9"

s_auto_reply_enable = True
# 初始化机器人，扫码登陆
bot = Bot(cache_path=True, console_qr = False, qr_path='robot.png')
tuling = Tuling(api_key=TULIN_TOKEN)

def get_friend(name):
    #通过机器人对象 Bot 的 chats(), friends()，groups(), mps() 方法, 可分别获取到当前机器人的 所有聊天对象、好友、群聊，以及公众号列表
    #回复 my_friend 的消息 (优先匹配后注册的函数!)
    #print(bot.friends())
    try:
        my_friend = bot.friends().search(name)[0]
    except:
        print('can not find friend')
        my_friend = ''
    print('friend:', my_friend)
    return my_friend


def process_msg_from_friend(name):
    #注册好友回复信息
    my_friend = get_friend(name)
    @bot.register(my_friend)
    def reply_my_friend(msg):
        print(msg)
        #tuling.do_reply(msg)


# 调用图灵机器人API，发送消息并获得机器人的回复
def tuling_reply(msg_content, user_id):
    url_api = 'http://www.tuling123.com/openapi/api'
    data = {
            'key' : TULIN_TOKEN,
            'info' : msg_content,
            'userid' : user_id,
            }

    print("use Tuling reply")
    s = requests.post(url_api, data=data).json()
    print('return code: ' + str(s['code']), str(s['text']))
    if s['code'] == 100000:
        return '[robot]:' + s['text']
    if s['code'] == 200000:
        return '[robot]:' + s['text'] + s['url']
    if s['code'] == 302000:
        news = random.choice(s['list'])
        return '[robot]:' + news['article'] + '\n' + news['detailurl']
    if s['code'] == 308000:
        menu = random.choice(s['list'])
        return '[robot]:' + menu['name'] + '\n' + menu['detailurl'] + '\n' + menu['info']

#茉莉
def moli_reply(msg_content):
    moli_data = {
        "question" : msg_content,
        "api_key" : MOLI_TOKEN,
        "api_secret" : "anaoutswrz1y"
    }
    moli_api_url = 'http://i.itpk.cn/api.php'
    m = requests.post(moli_api_url, data = moli_data)
    print('moli:', m.text)
    return '[robot]:' + m.text


def emotions_reply(keyword):
    print("try gif reply...")
    res = requests.get('https://www.doutula.com/search', {'keyword': keyword})
    html = etree.HTML(res.text)
    urls = html.xpath('//div[@class="image-container"][1]//img[contains(@class, "img-responsive")]/@data-original')
    if len(urls) < 1:
        raise Exception('doutula cannot reply this message')
        url = 'http:' + random.choice(urls)

        return url


def auto_reply(msg, robot='tuling'):
    if robot == 'tuling':
        return tuling_reply(msg.text, msg.sender.pui)
    else:
        return moli_reply(msg.text)


def my_info():
    # 获取所有好友[返回列表包含Chats对象(你的所有好友，包括自己)]
    t0 = bot.friends(update=False)
    # 查看自己好友数(除开自己)
    print("我的好友数："+str(len(t0)-1))

    # 获取所有微信群[返回列表包含Groups对象]
    t1 = bot.groups(update=False)
    # 查看微信群数(活跃的)
    print("我的微信群聊数："+str(len(t1)))

    # 获取所有关注的微信公众号[返回列表包含Chats对象]
    t2 = bot.mps(update=False)
    # 查看关注的微信公众号数
    print("我关注的微信公众号数："+str(len(t2)))


def get_msg_from_myself():
    # 似乎是微信做了限制，无法用robot给自己发消息,  只能获取
    @bot.register(bot.self, except_self=False)
    def reply_self(msg):
        print(msg)
        if msg.text == '芝麻开门':
            print('启动')
            s_auto_reply_enable = True
        elif msg.text == '芝麻关门':
            print('关闭')
            s_auto_reply_enable = False
        elif '芝麻加人：' in msg.text:
            print('加人')
            try:
                modify_auto_name_to_json('add', 'friends', msg.text.split('：')[1])
            except Exception as e:
                print('msg:', e)
                return
        elif '芝麻减人：' in msg.text:
            print('减人')
            try:
                modify_auto_name_to_json('del', 'friends', msg.text.split('：')[1])
            except Exception as e:
                print('msg:', e)
                return
        elif '芝麻加群：' in msg.text:
            print('加群')
            try:
                modify_auto_name_to_json('add', 'groups', msg.text.split('：')[1])
            except Exception as e:
                print('msg:', e)
                return
        elif '芝麻减群：' in msg.text:
            print('减群')
            try:
                modify_auto_name_to_json('del', 'groups', msg.text.split('：')[1])
            except Exception as e:
                print('msg:', e)
                return
        else:
            text = moli_reply(msg.text)
            #print('reply:', text)
            bot.file_helper.send(text)


def is_the_groups(msg):
    names = get_auto_groups_and_friends()['groups']
    print('groups:', names)
    print('NickName:', msg.chat.raw['NickName'])
    for name in names:
        if msg.chat.raw['NickName'] == name:
            print('hit .', name)
            if msg.is_at:
                #print('get @')
                return True
    return False


def get_all_msg():
    #注册消息使用简单的@bot.register()方法
    # 打印来自其他好友、群聊和公众号的消息
    @bot.register()
    def print_others(msg):
        #print('chat:', msg.chat) #group
        #print('----:', msg.chat.__dict__)
        #print(msg.member.__dict__)
        print(msg)


def process_groups_my_msg():
    # 打印出所有群聊中@自己的文本消息，并自动回复相同内容
    # 这条注册消息是我们构建群聊机器人的基础
    @bot.register(Group)
    def print_group_msg(msg):
        if msg.is_at:
            print('group:', msg.chat) #group
            print(msg)
            if is_the_groups(msg):
                if s_auto_reply_enable:
                    text = auto_reply(msg)
                    msg.reply(text)
                    #tuling.do_reply(msg)


def process_user_msg():
    # 响应好友消息
    @bot.register([Friend], msg_types=TEXT)
    def exist_friends(msg):
        print(msg)
        #print(msg.chat.name, msg.chat.nick_name)
        names = get_auto_groups_and_friends()['friends']
        print('friends:', names)
        if msg.chat.name in names:
            print('hit:', msg.chat.name)
            if s_auto_reply_enable:
                text = auto_reply(msg)
                msg.reply(text)


def get_auto_groups_and_friends():
    ret = {}
    ret['friends'] = []
    ret['groups'] = []
    try:
        resFp = open('./data.json', "r", encoding='utf-8')
        jsonData = json.load(resFp)
        #strJson = json.dumps(jsonData, ensure_ascii=False)
        #print(strJson)
        resFp.close()
    except Exception as e:
        jsonData = {}
        print('json is empty:', e)
        return ret

    ret['friends'] = jsonData['friends']
    ret['groups'] = jsonData['groups']
    return ret


def modify_auto_name_to_json(op, which, name):
    try:
        resFp = open('./data.json', "r", encoding='utf-8')
        jsonData = json.load(resFp)
        resFp.close()
        if which != 'friends' and which != 'groups':
            print('err', which, name)
            return
        if name in jsonData[which]:
            if op == 'del':
                jsonData[which].remove(name)
                print('del', name)
        else:
            if op == 'add':
                jsonData[which].append(name)
                print('add', jsonData[which])

        strJson = json.dumps(jsonData, ensure_ascii=False)
        #print(strJson)
        with open('./data.json', 'w', encoding='utf-8') as of:
            of.write(strJson)

    except Exception as e:
        print('json:', e)
        return


if __name__ == '__main__':
    my_info()
    get_msg_from_myself()
    process_groups_my_msg()
    process_user_msg()

    #print(tuling_reply('天气', '512583'))
    #moli_reply('天气')
    #print(get_auto_groups_and_friends())

    # 进入Python命令行，让程序保持运行
    embed()
    # 阴塞线程
    #bot.join()
