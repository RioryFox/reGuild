if not __name__ == "__main__":
    
    import math
    import time
    import vk_api
    from func import log_and_print
    from vk_api.longpoll import VkEventType
    from config import my_chat_id
    from config import my_token

def filter_events(long_pool, my_api, debug=False):

    chats_events = []
    users_events = []
    result = {"process": "#filter_events", "sucsess": True, "error": None, "data": None}
    #Участок отвечающий за сортировку входящих событий, если нам важно проверить какое-то событие, то мы сохраняем его в стэк

    #~~~~~~~~~~~~~~~~~
    try:

        for api_event in long_pool.listen():

            if api_event.type == VkEventType.MESSAGE_NEW:
                if api_event.from_chat:
                    if api_event.chat_id == my_chat_id or api_event.user_id == -183040898:
                        chats_events.append((api_event.chat_id, api_event.user_id, api_event.text, api_event.message_id, api_event, True, True))
                elif api_event.from_user:
                    users_events.append((api_event.user_id, api_event.text, api_event.message_id, api_event, True, True))

            #Поддержка работоспособности
            #~~~~~~~~~~~~~~~~~
            if math.ceil(time.time()) % 10 in [3]:
                _ = my_api.users.get() #костыль для незакрытия соединения!!!

            if len(chats_events) > 0 or len(users_events) > 0:
                break

    except Exception as error:
        my_session = vk_api.VkApi(token=my_token)
        my_api = my_session.get_api()
    log_and_print(result, debug)
    return {"chats": chats_events, "users": users_events}

