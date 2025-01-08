if  not __name__ == "__main__":
    import requests
    import user_agent
    from bs4 import BeautifulSoup
    from config import dungeon_token
    import json
else:
    raise Exception("is is a libray, not a main file!")

def check_red_books(item_id):
    url = f"https://vip3.activeusers.ru/app.php?act=item&id={item_id}&auth_key={dungeon_token}&viewer_id=878366772&group_id=182985865&api_id=7055214&back=act:user"
    my_user_agent = user_agent.generate_navigator()
    result = requests.get(url, headers=my_user_agent)
    soup = BeautifulSoup(result.text)
    #print(soup.prettify())
    print(result.json())


#check_red_books(13609)