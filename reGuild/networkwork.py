if  not __name__ == "__main__":
    import requests
    import user_agent
    from bs4 import BeautifulSoup
    from config import dungeon_token
    import json
    import re
    import random
    import time
    import math
    from db_work import *
    from func import log_and_print
else:
    raise Exception("is is a libray, not a main file!")


def check_price(item_id, debug=False):
    result = {"process": "#check_price", "sucsess": True, "error": None, "data": None}

    session = requests.Session()
    url = f"https://vip3.activeusers.ru/app.php?act=item&id={item_id}&auth_key={dungeon_token}&viewer_id=sudaid&group_id=182985865&api_id=7055214&back=act:user"

    my_user_agent = user_agent.generate_navigator()
    answer = session.get(url, headers=my_user_agent)
    text = str(answer.content)
    for line in answer.iter_lines(decode_unicode=True):
        text += str(line.strip())
    name = re.findall(r"История цен аукциона на ([^\"]+)',backgroundColor:", text)
    cost = []
    if name:
        cost = re.findall(r'\[(\d+),(\d+)\]', text)
    else:
        name = "Uncknown"
    return name, cost


def get_global_ids():
    
    session = requests.Session()
    url = "https://vip3.activeusers.ru/app.php?act=shop&auth_key={dungeon_token}&viewer_id=sudaid&group_id=182985865&api_id=7055214"
    my_user_agent = user_agent.generate_navigator()
    answer = session.get(url, headers=my_user_agent)
    all_ids = re.findall(r'/app\.php\?act=item&id=(\d+)&auth_key=[a-zA-Z0-9]+&viewer_id=\d+&group_id=\d+&api', str(answer.content))
    for line in answer.iter_lines(decode_unicode=True):
        all_ids += re.findall(r'/app\.php\?act=item&id=(\d+)&auth_key=[a-zA-Z0-9]+&viewer_id=\d+&group_id=\d+&api', line.strip())
    all_ids = list(set(all_ids))
    return all_ids

def get_global_prices():
    ids = get_global_ids()

    for id in ids:
        Name, Prices = check_price(id)
        time.sleep(0.3)
        if len(Prices) > 0:
            result = sql_sget("main_base\\items.db", "items", {'id' : id, 'name' : Name[0], 'smalname' : Name[0].lower().replace('книга - ', '')}, check=True)
            log_and_print(result, True)


#get_global_prices()