if __name__ == "__main__":

    #-------------Work with system
    import os
    import sys

    #-------------Work with timers and math
    import time
    import math
    import multiprocessing
    import datetime

    #-------------Work with strings
    import string

    #-------------Work with save data
    import sqlite3
    import json
    import logging
    
    #------------Data string/html/css analise
    import re 
    import Levenshtein
    from bs4 import BeautifulSoup

    #------------Work with Ethernet
    import requests
    import vk_api
    from vk_api.longpoll import VkLongPoll, VkEventType

    #-------------My libraries
    from func import *
    from config import *
    from db_work import *
    from frame_work import filter_events
    from networkwork import *

else:

    raise Exception("\x1b[34mThis is main file, not a library!")
#-------------------------------------------------------------
class MyLongPoll(VkLongPoll):

    def listen(self):

        while True:

            try:

                for event in self.check():

                    yield event

            except Exception as error:

                print(f"Переподключение к серверам ВК - {error}\n")
                result = 0

                while result != 200:

                    try:
                        result = requests.get("https://yandex.ru").status_code

                    except Exception:
                        continue

                print("\n--\x1b[32mCоnnection\x1b[m--\n")
                my_session = vk_api.VkApi(token=my_token)
                my_api = my_session.get_api()
                self.__init__(my_session)
                continue

#-------------------------------------------------------------

#Загрузка и подключение к вк от имени человека
#~~~~~~~~~~~~~~~~~
my_session = vk_api.VkApi(token=my_token)
my_api = my_session.get_api()
long_pool = MyLongPoll(vk=my_session)
my_id = my_api.users.get()[0]["id"]
my_send = False

#Загрузка и подключение к вк от имени группы
#~~~~~~~~~~~~~~~~~
guild_session = vk_api.VkApi(token=guild_token)
guild_api = guild_session.get_api()
guild_send = False

#-------------------------------------------------------------

#"Стэки"
#~~~~~~~~~~~~~~~~~
chats_events = []
users_events = []

#Запуск баз данных, проверки целостности
#~~~~~~~~~~~~~~~~~
creat_tables(my_id)
#get_global_prices()
#send_msg(my_session, "chat", my_chat_id, "мой профиль")
all_items = get_all_items()
all_items = [item for sublist in all_items['data'] for item in sublist]


#-------------------------------------------------------------


while True:
    print('sycle')

    #Участок отвечающий за сортировку входящих событий, если нам важно проверить какое-то событие, то мы сохраняем его в стэк
    #~~~~~~~~~~~~~~~~~
    filter = filter_events(long_pool, my_api)
    chats_events = filter["chats"]
    users_events = filter["users"]
    guild_msg = ""
    my_msg = ""
    guild_send = False
    my_send = False

    #Обработка событий из чатов, которые мы уже отобрали и считаем важными
    #~~~~~~~~~~~~~~~~~
    while len(chats_events) > 0 and not (guild_send or my_send):
        result = {"process": "#chats_events", "sucsess": True, "error": None, "data": None}

        try:

            #Выгружаем данные в переменные
            #~~~~~~~~~~~~~~~~~
            (chat_id, user_id, msg, my_msg_id, api_event, my_send, guild_send) = chats_events[0]

            try:
                user_data = my_api.users.get(user_ids=[user_id])[0]
            except Exception as error:
                user_data = None

            my_msg_id = api_event.message_id
            litle_msg = msg.lower()

            #Участок отвечающий за рекцию на событие из чата
            #~~~~~~~~~~~~~~~~~
            if chat_id == my_chat_id:

                if litle_msg == "пинг":
                    print(guild_msg)
                    guild_msg = "Понг!"
                    
                elif user_id == -183040898:
                    if ", ваш профиль:" in litle_msg:

                        info = read_profile(msg)
                        user_id = info["data"]["userid"]
                        user_data = my_api.users.get(user_ids=[user_id])[0]
                        old_data = sql_sget("main_base\\users.db", "profile", {"userid" : user_id})

                        if old_data["data"] is None:
                            new_data = sql_sget("main_base\\users.db", "profile", info["data"], check=True)
                            guild_msg = "Поздравляю, вы успешно зарегистрированы в системе..."

                        else:  
                            old_data = old_data["data"]
                            new_data = sql_update("main_base\\users.db", "profile", info["data"])['data'][0]

                            guild_msg += f" 🌐[id{user_id}|{user_data['first_name']}] до {new_data[6]+1} Уровня: "
                            guild_msg += f"\n🖐️+👊: {new_data[6]*6+90} ❤️: {new_data[6]*3+45}"
                            guild_msg += f"\n👊: {new_data[7]-old_data[7]} "
                            guild_msg += f"🖐️: {new_data[8]-old_data[8]} "
                            guild_msg += f"❤️: {new_data[9]-old_data[9]} "
                            guild_msg += f"💀: {new_data[6]-old_data[6]}"
                elif litle_msg.startswith('чистыми '):
                    guild_msg = 'Не верный запрос'
                    if re.findall(r'чистыми о (\d+)', litle_msg):
                        guild_msg = str(math.ceil(int(re.findall(r'чистыми о (\d+)', litle_msg)[0])/0.95))
                        guild_msg = f"{guild_msg} осколков"
                    elif re.findall(r'чистыми (\d+)', litle_msg):
                        guild_msg =str(math.ceil(int(re.findall(r'чистыми (\d+)', litle_msg)[0])/0.9))
                        guild_msg = f"{guild_msg} золота"
                elif litle_msg.startswith('грязными '):
                    guild_msg = 'Не верный запрос'
                    if re.findall(r'грязными о (\d+)', litle_msg):
                        guild_msg = re.findall(r'грязными о (\d+)', litle_msg)[0]
                    elif re.findall(r'грязными (\d+)', litle_msg):
                        guild_msg = re.findall(r'грязными (\d+)', litle_msg)[0]
                elif litle_msg == "мое пиво":
                    data = sql_sget("main_base\\users.db", "users", {"userid" :user_id}, check=True)["data"][2]
                    guild_msg = f'У вас денег на пиво {data}'
                    #~~~~~~~~~~~~~~~~~
                elif litle_msg.startswith('цена '):
                    print(175)
                    item = litle_msg[5:].lower()
                    if item not in all_items:
                        item = give_chance(item, all_items)
                        print(item)
                    guild_msg = "Я не нашел такого предмета!"
                    if item is not None:
                        result = sql_sget("main_base\\items.db", "items", {'smalname' : item})
                        if result['data'] is not None:
                            guild_msg = str(result['data'])
                    
                else:
                    guild_send = False 

            else:

                if user_id == -183040898:
                    if ", ваш профиль:" in litle_msg:

                        info = read_profile(msg)
                        user_id = info["data"]["userid"]
                        user_data = my_api.users.get(user_ids=[user_id])[0]
                        old_data = sql_sget("main_base\\users.db", "profile", {"userid" : user_id})

                        if old_data["data"] is None:
                            new_data = sql_sget("main_base\\users.db", "profile", info["data"], check=True)
                            guild_msg = "Поздравляю, вы успешно зарегистрированы в системе..."

                        else:
                            old_data = old_data["data"]
                            new_data = sql_update("main_base\\users.db", "profile", info["data"])['data'][0]

            #Участок отвечающий за реакцию человека на событие из чата
            #~~~~~~~~~~~~~~~~~
            if chat_id == my_chat_id:
                if litle_msg == "пинг":
                    my_msg = "Понг!"
                else:
                    my_send = False

            if my_send:
                result['data'] = guild_msg

        except Exception as error:

            result["sucsess"] = False
            result["error"] = error

        log_and_print(result, False)
        #Очистка
        #~~~~~~~~~~~~~~~~~
        chats_events.remove(chats_events[0])

    

    #Обработка событий от пользователей, которых мы считем важными 
    #~~~~~~~~~~~~~~~~~
    while len(users_events) > 0 and not (guild_send or my_send):
        result = {"process": "#users_events", "sucsess": True, "error": None, "data": None}

        try:
            #Выгружаем данные в переменные
            #~~~~~~~~~~~~~~~~~
            (my_chat_id, text, my_msg_id, api_event, my_send, guild_send) = users_events[0]

            #Участок отвечающий за реакцию человека на событие
            #~~~~~~~~~~~~~~~~~
            _ = None

        except Exception as error:
            result["sucsess"] = False
            result["error"] = error

        log_and_print(result, True)
        #Отправка сообщений
        #~~~~~~~~~~~~~~~~~
        _ = None

        #Очистка
        #~~~~~~~~~~~~~~~~~
        users_events.remove(users_events[0])

    #Отправка сообщений
    #~~~~~~~~~~~~~~~~~
    if guild_send and len(guild_msg) > 0:

        guild_msg_id = search_txt_in_msg(guild_api, msg, guild_chat_id, user_id, int(api_event.datetime.timestamp()))

        if guild_msg_id["sucsess"]:
            guild_msg_id = guild_msg_id["data"]["id"]
        else:
            guild_msg_id = None

        send_msg(guild_session, "chat", guild_chat_id, guild_msg, reply_to=guild_msg_id)
        guild_send = False

    if my_send and len(my_msg) > 0:

        send_msg(my_session, "chat", my_chat_id, my_msg, reply_to=my_msg_id)
        my_send = False

    #страховка
    users_events = []
    chats_events = []