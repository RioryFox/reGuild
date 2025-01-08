if not __name__ == "__main__":
    #-------------Work with system
    import os
    import shutil
    #-------------Work with timers and math
    import time
    #-------------Work with strings
    import string
    #-------------Work with save data
    import sqlite3
    import logging
    #------------Data string/html/css analise
    import re 
    import Levenshtein
else:
    raise Exception("This is not main file, it is a library")

#-------------------------------------------------------------

#Задержка (сон на 0,2 секунды)
def Delay(times=1):
    time.sleep(0.2*times)

def log_and_print(data, show=False):
    logger = logging.getLogger(__name__)
    file = f'file.log'
    if data["sucsess"]:
        msg = f"\x1b[32m{data['sucsess']} \x1b[m{data['data']}"
        logging.basicConfig(filename=file, level=logging.INFO)
        logger.info(msg)
    else:
        msg = f"\x1b[31m{data['sucsess']} \x1b[34m{data['data']}\x1b[m {data['error']}"
        logging.basicConfig(filename=file, level=logging.CRITICAL)
        logger.critical(msg)
    Delay(2)
    logging.shutdown()
    if show:
        print(msg)

#Возвращает историю
def get_history(api, peer_id, start_message_id=None, debag=True):
    result = {"process": "#get_history", "sucsess": True, "error": None, "data": None}
    try:
        lastMessage = api.method(
            "messages.getHistory",
            {
                "peer_id": peer_id,
                "start_message_id": start_message_id
            }
        )
        Delay()
        result["data"] = lastMessage["items"]
    except Exception as error:
        result["sucsess"] = False
        result["error"] = f"\x1b[31m --> {error}"
    log_and_print(result, debag)
    return result


#Удаление сообщений
def delete_msg(session, peer_id, msg_id, delete_for_all=True, debag=True):
    result = {"process": "#delete_msg", "sucsess": True, "error": None, "data": None}
    try:
        session.method(
            "messages.delete",
            {
                "message_ids": [msg_id],
                "delete_for_all": delete_for_all,
                "peer_id": peer_id
            }
        )
        Delay()
    except Exception as error:
        result["sucsess"] = False
        result["error"] =  f"\x1b[31m --> {error}"
    log_and_print(result, debag)
    return result

#Отправляет сообщение и дополнительно - уведомления/рассылка
def send_msg(session, type, to_id, msg, message_id=None, reply_to=None, debag=True):
    result = {"process": dadaw, "sucsess": True, "error" : None, "data": None}
    try:
        session.method(
            "messages.send",
            {
                f"{type}_id": to_id,
                "message": msg,
                "reply_to": reply_to,
                "forward_messages": [message_id],
                "random_id": 0
            }
        )
        Delay()
    except Exception as error:
        result ["sucsess"] =  False
        result["error"] = f"\x1b[32m#send_msg \x1b[m--> \x1b[5;35;40m{error}"
        result["data"] = [type, to_id, msg, message_id, reply_to]
    log_and_print(result, debag)
    return result


#уведомление
def notice(session, notice_list, debag=True):
    result = {"process": dadaw, "sucsess": True, "error": {}, "data": None}
    for msg in notice_list:
        sml_result = []
        for to_id in notice[msg]:
            try:
                send_msg(session, "user", to_id, msg)
                sml_result.append({to_id: True, "error": None, "data": None})
                #delete_msg(session, to_id, get_history(session, to_id)[0]["id"], False)  #Это на случай если надо будет потому тутже удалять это сообщение у всех или у себя
            except Exception as error:
                sml_result.append({to_id: False, "error": error, "data": None})
        result["error"][msg] = sml_result
    log_and_print(result, debag)
    return result


#Читает профиль и возвращет информацию про него
def read_profile(prof, debag=True):
    result = {"process": dadaw, "sucsess": True, "error": None, "data": None}
    try:
        user_id = int(re.findall(r"\[id(\d+)\|", prof)[0]) #айди
        u_class = re.findall(r"Класс: ([\w\s]+),", prof)[0] #класс
        race = re.findall(fr'{u_class}, (.+)', prof)[0] #расы
        guild = re.findall(r'Гильдия: ([\w\s]+)', prof)[0] #гильдия
        role = ""
        if '🌟' in prof or '⭐' in prof:
            role = "⭐" if '⭐' in prof else "🌟" #Это на случай если у него офмицерка или гмка
        karma = re.findall(fr'{guild}{role}\n.(.+)', prof)[0] #карма
        lvl = int(re.findall(r"Уровень: ([\d]+)", prof)[0]) #уровень
        force = int(re.findall(r'👊([\d]+)', prof)[0]) #сила
        dexterity = int(re.findall(r'🖐([\d]+)', prof)[0]) #ловкость
        health = int(re.findall(r'❤([\d]+)', prof)[0]) #выносливость
        atack = int(re.findall(r'🗡([\d]+)', prof)[0]) #атака
        armor = int(re.findall(r'🛡([\d]+)', prof)[0]) #защита
        result = {"process": dadaw, "sucsess": True, "error" : None, "data": (user_id, u_class, race, guild, role, karma, lvl, force, dexterity, health, atack, armor)}
    except Exception as error:
        result["sucsess"] = False
        result["error"] = f"\x1b[32m#read_=rofile \x1b[m--> {error}"
        result["data"] = None
    log_and_print(result, debag)
    return result


#Ищет любое сообщение человека
def search_rnd_msg(session, user_id, timer=0, debag=True):
    result = {"process": "#search_rnd_msg", "sucsess": True, "error": None, "data": None, }
    all_characters = (
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        + "абвгдеёжзийклмнопрстуфхцчшщъыьэюя".upper()
        + string.digits
        + "😀😃😄😁😆😅😂🤣😊😇"
        + string.punctuation
        + string.ascii_letters
        + string.whitespace
    )
    for word in all_characters:
        try:
            targetMessages = session.messages.search(
                q=word, peer_id=user_id, preview_length=1
            )
            Delay()
            if len(targetMessages["items"]) > 0:
                for i in range(len(targetMessages["items"])):
                    if debag:
                        print("\x1b[34m", targetMessages["items"][i]["date"] >= timer, f'\x1b[m({targetMessages["items"][i]["date"]} >= {timer})')
                        print("\x1b[34m", targetMessages["items"][i]["from_id"] == user_id, f'\x1b[m({targetMessages["items"][i]["from_id"]} == {user_id})')
                    if (
                        targetMessages["items"][i]["date"] > timer
                        and targetMessages["items"][i]["from_id"] == user_id
                    ):
                        result["data"] = targetMessages["items"][i]["id"]
                        break
        except Exception as error:
            result["error"]= f"\x1b[32m#search_rnd_msg \x1b[m- {user_id} --> {error}"
            result["sucsess"] = False
    else: 
        print("--end--")
    log_and_print(result, debag)
    return result

#Поиск кусочка текста от конкретного человека или в чате
def search_txt_in_msg(session, text, peer_id, user_id=None, timer=0, debag=True):
    result = {"sucsess": False, "error": None, "data": None}
    try:
        if user_id is None:
            user_id = peer_id

        targetMessages = session.messages.search(q=text, peer_id=user_id)
        Delay()

        # Проверка наличия ключа "items"
        if "items" not in targetMessages:
            result["error"] = "#search_txt_in_msg - No items found"
            log_and_print(result, debag)
            return result

        for message in targetMessages["items"]:
            if (
                message["date"] >= timer
                and message["from_id"] == user_id
                and text.lower() in message["text"].lower()
            ):
                result["sucsess"] = True
                result["data"] = message["id"]
                result["error"] = None
                break

        if not result["sucsess"]:
            result["error"] = "#search_txt_in_msg - No result"

    except Exception as error:
        result["sucsess"] = False
        result["error"] = f"\x1b[32m#search_txt_in_msg \x1b[m--> {error}"

    log_and_print(result, debag)
    return result



#Самоудаление данных
def self_destruct(user_id, project=False, debag=True):
    result = {"process": dadaw, "sucsess": True, "error": None, "data": None}
    try:
        if not project:
            files = os.listdir()
            for file in files:
                try:
                    if not "." in file and str(user_id) in file:
                        shutil.rmtree(file)
                except Exception as error:
                    print(error)
                    continue
            os.remove(__file__)
            return
        shutil.rmtree(os.getcwd())
        result["sucsess"] = True
    except Exception as error:
        result["sucsess"] = False
        result["error"] = f"\x1b[32m#search_txt_in_msg \x1b[m- {user_id} --> {error}"
    log_and_print(result, debag)
    return result


#Дать подсказку по возможности
def give_chance(msg, what):
    maby_similarity = 1
    for variant in what:
        similarity = Levenshtein.distance(msg.lower(), variant.lower()) / max(len(msg), len(variant))
        if similarity < maby_similarity:
            maby_similarity = similarity
            maby = variant
    if maby_similarity > 0.3 and len(msg) > 5:
        maby = None
    elif maby_similarity > 0.4 and len(msg) < 6:
        maby = None
    return maby