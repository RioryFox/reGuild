if not __name__ == "__main__":
    #-------------Work with system
    import os
    from shutil import rmtree
    #-------------Work with timers and math
    import time
    #-------------Work with strings
    import string
    #-------------Work with save data
    import logging
    #------------Data string/html/css analise
    import re 
    import Levenshtein
    import vk_api
    from vk_api import VkUpload
else:
    raise Exception("This is not main file, it is a library")

#-------------------------------------------------------------

#Задержка (сон на 0,1 секунды)

def log_and_print(data, show=False):
    logger = logging.getLogger(__name__)
    file = f'file.log'
    msg = f'\x1b[36;2m{data["process"]} \x1b[m--> '
    if data["sucsess"]:
        msg += f"\x1b[32m{data['sucsess']} \x1b[m{data['data']}"
        logging.basicConfig(filename=file, level=logging.INFO)
        logger.info(msg)
    else:
        msg += f"\x1b[31m{data['sucsess']} \x1b[34m{data['data']}\x1b[m {data['error']}"
        logging.basicConfig(filename=file, level=logging.ERROR)
        logger.error(msg)
    logging.shutdown()
    if show:
        print(msg)

#Возвращает историю
def get_history(api, peer_id, start_message_id=None, debug=True):
    result = {"process": "#get_history", "sucsess": True, "error": None, "data": None}
    try:
        lastMessage = api.method(
            "messages.getHistory",
            {
                "peer_id": peer_id,
                "start_message_id": start_message_id
            }
        )
        result["data"] = lastMessage["items"]
    except Exception as error:
        result["sucsess"] = False
        result["error"] = error
    log_and_print(result, debug)
    return result


#Удаление сообщений
def delete_msg(session, peer_id, msg_id, delete_for_all=True, debug=True):
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
    except Exception as error:
        result["sucsess"] = False
        result["error"] = error
    log_and_print(result, debug)
    return result

#Отправляет сообщение и дополнительно - уведомления/рассылка
def send_msg(session, type, to_id, msg="", message_id=[], attachment=None, reply_to=None, debug=True):
    result = {"process": "#send_msg", "sucsess": True, "error" : None, "data": None}
    if attachment is not None and "." in attachment:
        upload = vk_api.upload.VkUpload(session)
        obj = upload.document(attachment)
        attachment = f"doc{session.get_api().users.get()[0]['id']}_{obj['doc']['id']}"
    print(attachment)
    try:
        session.method(
            "messages.send",
            {
                f"{type}_id": to_id,
                "message": msg,
                "attachment": attachment,
                "reply_to": reply_to,
                "forward_messages": message_id,
                "random_id": 0
            }
        )
    except Exception as error:
        result ["sucsess"] =  False
        result["error"] = error
        result["data"] = [type, to_id, msg, message_id, reply_to]
    log_and_print(result, debug)
    return result


#уведомление
def notice(session, notice_list, debug=True):
    result = {"process": "#notice", "sucsess": True, "error": {}, "data": None}
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
    log_and_print(result, debug)
    return result


#Читает профиль и возвращет информацию про него
def read_profile(prof, debug=False):
    result = {"process": "#read_profile", "sucsess": True, "error": None, "data": None}
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
        attack = int(re.findall(r'🗡([\d]+)', prof)[0]) #атака
        armor = int(re.findall(r'🛡([\d]+)', prof)[0]) #защита
        result["data"] = {
            "userid": user_id,
            "class": u_class,
            "race": race,
            "guild": guild,
            "role": role,
            "karma": karma,
            "lvl": lvl,
            "force": force,
            "dexterity": dexterity,
            "health": health,
            "attack": attack,
            "armor": armor
        }
    except Exception as error:
        result["sucsess"] = False
        result["error"] = error
    log_and_print(result, debug)
    return result


#Ищет любое сообщение человека
def search_rnd_msg(session, user_id, timer=0, debug=True):
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
            if len(targetMessages["items"]) > 0:
                for i in range(len(targetMessages["items"])):
                    if (
                        targetMessages["items"][i]["date"] > timer
                        and targetMessages["items"][i]["from_id"] == user_id
                    ):
                        result["data"] = targetMessages["items"][i]["id"]
                        break
        except Exception as error:
            result["error"]= error
            result["sucsess"] = False
    else: 
        print("--end--")
    log_and_print(result, debug)
    return result

#Поиск кусочка текста от конкретного человека или в чате
def search_txt_in_msg(session, text, peer_id, user_id=None, timer=0, debug=False):
    result = {"process": "#search_txt_in_msg", "sucsess": False, "error": None, "data": None}
    try:
        if user_id is not None and peer_id is not None:
            peer_id+=2000000000

        targetMessages = session.messages.search(q=text, peer_id=peer_id)

        # Проверка наличия ключа "items"
        if "items" not in targetMessages:
            result["error"] = "No items found"

        else:
            for message in targetMessages["items"]:
                if (
                    message["date"] >= timer
                    and message["from_id"] == user_id
                    and text.lower() in message["text"].lower()
                ):
                    result["sucsess"] = True
                    result["data"] = message
                    result["error"] = None
                    break

        if not result["sucsess"] and result["error"] is not None:
            result["error"] = "No result"

    except Exception as error:
        result["sucsess"] = False
        result["error"] = error

    log_and_print(result, debug)
    return result

def fast_search(session, text, peer_id, user_id=None, timer=0, debug=False):
    result = {"process": "#search_txt_in_msg", "sucsess": False, "error": None, "data": None}
    #history = 


#Самоудаление данных
def self_destruct(user_id, project=False, debug=True):
    result = {"process":f"#self_destruct", "sucsess": True, "error": None, "data": None}
    try:
        if not project:
            files = os.listdir()
            for file in files:
                try:
                    if not "." in file and str(user_id) in file:
                        rmtree(file)
                except Exception as error:
                    print(error)
                    continue
            os.remove(__file__)
            return
        rmtree(os.getcwd())
        result["sucsess"] = True
    except Exception as error:
        result["sucsess"] = False
        result["error"] = error
    log_and_print(result, debug)
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