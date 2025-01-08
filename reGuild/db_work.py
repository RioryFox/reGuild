if not __name__ == "__main__":
    #-------------Work with system
    import os
    #-------------Work with save data
    import sqlite3
    import json
    #
    from func import Delay
else:
    raise Exception("This is not main file, it is a library")

def creat_tables(me_id):
    result = True
    try:
        for floder in ["main_base"]:
            if not os.path.exists(floder):
                print(f"\x1b[34m(@id{me_id})\x1b[32m CREATE FLODER: \x1b[m{floder}")
                os.mkdir(floder)
                Delay()
        if not os.path.exists("main_base\\users.db"):
            print(f"\x1b[34m(@id{me_id})\x1b[32m CREATE DB-SQLITE\x1b[m")
            with sqlite3.connect("main_base\\users.db") as db:
                cursor = db.cursor()
                query = """
                CREATE TABLE IF NOT EXISTS users(
                userid INTEGER, 
                roots INTEGER DEFAULT 0 ,
                balance INTEGER DEFAULT 0,
                spend_limit INTEGER DEFAULT 100000, 
                items_order TEXT
                );
                CREATE TABLE IF NOT EXISTS sklad(
                item TEXT,
                id INTEGER,
                free BOOLEAN DEFAULT FALSE,
                price INTEGER,
                min_lim INTEGER DEFAULT 0,
                max_lim INTEGER DEFAULT 999999,
                many_now INTEGER DEFAULT 0
                )
                """
                cursor.executescript(query)
                db.commit()
    except Exception as error:
        print(f"#creat_tables --> {error}")
        result = False
    Delay()
    return result

def sql_save(file, table, data):
    result = {"process": "#sql_save", "sucsess": True, "error": None, "data": None}
    way = ""
    try:
        for obj in data:
            way += f"{obj}, "
        else:
            way = way[:len(way)-2]
        what = []
        for obj in data:
            what.append(data[obj])
        part = '?, '*len(what)
        with sqlite3.connect(file) as db:
            cursor = db.cursor()
            query = f"INSERT INTO {table} ({way}) VALUES ({part[:len(part)-2]})"
            cursor.execute(query, what)
            db.commit()
    except Exception as error:
        result["sucsess"] = False
        result["error"] = f"#sql_save --> {error}"
    Delay()
    return result

def sql_get(file, table, data, all=True):
    result = {"process": "#sql_get", "sucsess": True, "error": None, "data": None}
    part = ""
    for obj in data:
        part += f"{obj}=?, "
    else:
        part = part[:len(part)-2]
    what = []
    for obj in data:
        what.append(data[obj])
    query = f'SELECT * FROM {table} WHERE {part}'
    print(query, what)
    try:
        with sqlite3.connect(file) as db:
            cursor = db.cursor()
            cursor.execute(query, what)
            if all:
                alpha = cursor.fetchall()
            else:
                alpha = cursor.fetchone()
            result["data"] = alpha
    except Exception as error:
        result["sucsess"] = False
        result["error"] = f'#sql_get --> {error}'
    Delay()
    return result

def sql_sget(file, table, data, all=True, check=True):
    result = {"process": "#sql_sget", "sucsess": True, "error": None, "data": None}
    try:
        result["data"] = sql_get(file, table, data, all)["data"]
        if result["data"] is not None:
            print(105)
            return result
        if check:
            result["data"] = sql_save(file, table, data)
        result = sql_get(file, table, data, all)["data"]
    except Exception as error:
        result["sucsess"] = False
        result["error"] = f'#sql_get --> {error}'
    return result