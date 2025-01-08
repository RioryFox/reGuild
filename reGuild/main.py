if __name__ == "__main__":
    #-------------Work with system
    import os
    import sys
    import shutil
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
                    Delay(2)
                print("\n--\x1b[32mCOnnection--\x1b[m\n")
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

#Загрузка и подключение к вк от имени группы
#~~~~~~~~~~~~~~~~~
guild_session = vk_api.VkApi(token=guild_token)
guild_api = my_session.get_api()

#-------------------------------------------------------------

#"Стэки"
#~~~~~~~~~~~~~~~~~
chat_events = []
user_events = []

#Запуск баз данных, проверки целостности
#~~~~~~~~~~~~~~~~~
creat_tables(my_id)
print(sql_sget("main_base\\users.db", "users", {"userid": 890775441}))



#-------------------------------------------------------------

while True:
    #Участок отвечающий за сортировку входящих событий, если нам важно проверить какое-то событие, то мы сохраняем его в стэк
    #~~~~~~~~~~~~~~~~~
    try:
        for api_event in long_pool.listen():
            if api_event.type == VkEventType.MESSAGE_NEW:
                if api_event.from_chat:
                    if api_event.chat_id == my_chat_id:
                        chat_events.append((api_event.chat_id, api_event.user_id, api_event.text, api_event.message_id, api_event, True, True))
                elif api_event.from_user:
                    user_events.append((api_event.user_id, api_event.text, api_event.message_id, api_event, True, True))

            #Поддержка работоспособности
            #~~~~~~~~~~~~~~~~~
            if math.ceil(time.time())%5 == 0:
                _ = my_api.users.get() #костыль для незакрытия соединения!!!
                Delay()
            if len(chat_events) != 0 or len(user_events) != 0:
                break
    except Exception as error:
        print(f'#main_cycle - {error}')

    #Обработка событий из чатов, которые мы уже отобрали и считаем важными
    #~~~~~~~~~~~~~~~~~
    while len(chat_events) > 0:
        try:
            #Выгружаем данные в переменные
            #~~~~~~~~~~~~~~~~~
            (chat_id, user_id, msg, my_msg_id, api_event, my_send, guild_send) = chat_events[0]
            guild_msg_id = search_txt_in_msg(guild_api, msg, guild_chat_id, user_id, int(api_event.datetime.timestamp()))
            if guild_msg_id["sucsess"]:
                guild_msg_id = guild_msg_id["data"]
            else:
                guild_msg_id = None
            litle_msg = msg.lower()
            my_msg = ""
            guild_msg = ""

            #Участок отвечающий за рекцию на событие из чата
            #~~~~~~~~~~~~~~~~~
            if litle_msg == "пинг":
                guild_msg = "Понг!"
            else:
                guild_send = False

            #Участок отвечающий за реакцию человека на событие из чата
            #~~~~~~~~~~~~~~~~~
            if litle_msg == "пинг":
                my_msg = "Понг!"
            elif "вы положили" in litle_msg and "золота в казну" in litle_msg: # and user_id == -183040898:
                ser = int(re.findall(r'вы положили (\d+) золота', litle_msg)[0])
                money = math.ceil(int(re.findall(r"вы положили (\d+) золота", litle_msg)[0])/0.9)
                user_id = int(re.findall(r"\[id(\d+)\|", litle_msg)[0])
                my_msg = f"+баланс {money}"
                my_msg_id = search_txt_in_msg(my_api, f"положить {ser} золота", my_chat_id, user_id)["data"]
                print(106, my_msg_id)
            else:
                my_send = False
        except Exception as error:
            print(f"#chat_events --> {error}")

        #Отправка сообщений
        #~~~~~~~~~~~~~~~~~
        if guild_send:
            send_msg(guild_session, "chat", guild_chat_id, guild_msg, reply_to=guild_msg_id)
        if my_send:
            send_msg(my_session, "chat", my_chat_id, my_msg, reply_to=my_msg_id)
        
        #Очистка
        #~~~~~~~~~~~~~~~~~
        chat_events.remove(chat_events[0])
    
    #Обработка событий от пользователей, которых мы считем важными 
    #~~~~~~~~~~~~~~~~~
    while len(user_events) > 0:
        try:
            #Выгружаем данные в переменные
            #~~~~~~~~~~~~~~~~~
            (my_chat_id, text, my_msg_id, api_event, my_send, guild_send) = user_events[0]

            #Участок отвечающий за реакцию человека на событие
            #~~~~~~~~~~~~~~~~~
            _
        except Exception as error:
            print(f"#user_events --> {error}")

        #Отправка сообщений
        #~~~~~~~~~~~~~~~~~
        _

        #Очистка
        #~~~~~~~~~~~~~~~~~
        user_events.remove(user_events[0])