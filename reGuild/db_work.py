if not __name__ == "__main__":
    #-------------Work with system
    import os
    #-------------Work with save data
    import sqlite3
    import json
    #
    from func import log_and_print
else:
    raise Exception("This is not main file, it is a library")

def creat_tables(me_id, debug=False):
    result = {"process": "#creat_tables", "sucsess": True, "error": None, "data": None, "update": False, "new": False}
    
    try:

        for floder in ["main_base"]:
            if not os.path.exists(floder):
                print(f"\x1b[34m(@id{me_id})\x1b[32m CREATE FLODER: \x1b[m{floder}")
                os.mkdir(floder)

        if not os.path.exists("main_base\\users.db"):

            print(f"\x1b[34m(@id{me_id})\x1b[32m CREATE DB-SQLITE: users\x1b[m")
            with sqlite3.connect("main_base\\users.db") as db:
                cursor = db.cursor()
                query = """

                CREATE TABLE IF NOT EXISTS users (
                    userid INTEGER, 
                    roots INTEGER DEFAULT 0,
                    balance INTEGER DEFAULT 0,
                    spend_limit INTEGER DEFAULT 100000, 
                    items_order TEXT
                );

                CREATE TABLE IF NOT EXISTS profile (
                    userid INTEGER,
                    class TEXT,
                    race TEXT,
                    guild TEXT,
                    role TEXT,
                    karma INTEGER,
                    lvl INTEGER,
                    force INTEGER,
                    dexterity INTEGER,
                    health INTEGER,
                    attack INTEGER,
                    armor INTEGER
                );

                """
                cursor.executescript(query)
                db.commit()
        if not os.path.exists("main_base\\items.db"):

            print(f"\x1b[34m(@id{me_id})\x1b[32m CREATE DB-SQLITE: items\x1b[m")
            with sqlite3.connect("main_base\\items.db") as db:
                cursor = db.cursor()
                query = """

            CREATE TABLE IF NOT EXISTS items (
                name TEXT,
                smalname TEXT,
                id INTEGER,
                shortcost INTEGER DEFAULT 0 CHECK (shortcost >= 0),
                longcost INTEGER DEFAULT 0 CHECK (longcost >= 0)
            );

            CREATE TABLE IF NOT EXISTS auction (
                name TEXT,
                smalname TEXT,
                price DECIMAL(10,2) NOT NULL,
                start_time INTEGER,
                end_time INTEGER
            );

            CREATE TABLE IF NOT EXISTS sklad (
                name TEXT,
                smalname TEXT,
                id INTEGER,
                free BOOLEAN DEFAULT FALSE CHECK (free IN (TRUE, FALSE)),
                price INTEGER NOT NULL,
                min_lim INTEGER DEFAULT 0 CHECK (min_lim >= 0),
                max_lim INTEGER DEFAULT 999999 CHECK (max_lim > min_lim AND max_lim <= 999999),
                many_now INTEGER DEFAULT 0
            );


                """
                cursor.executescript(query)
                db.commit()

    except Exception as error:

        result["sucsess"] = False
        result["error"] = error

    log_and_print(result, debug)
    return result

def sql_save(file, table, data, debug=False):
    result = {"process": "#sql_save", "sucsess": True, "error": None, "data": None, "update": False, "new": False}

    if not data:
        result["sucsess"] = False
        result["error"] = "Data is empty"
        log_and_print(result, debug)
        return result

    columns = ", ".join(data.keys())
    values = list(data.values())
    placeholders = ', '.join(['?'] * len(values))

    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    try:

        with sqlite3.connect(file) as db:
            cursor = db.cursor()
            cursor.execute(query, values)
            db.commit()
            result["new"] = True 

    except Exception as error:

        result["sucsess"] = False
        result["error"] = error

    log_and_print(result, debug)
    return result


def sql_get(file, table, data, all=True, debug=False):
    result = {"process": "#sql_get", "sucsess": True, "error": None, "data": None}

    if not data:
        result["sucsess"] = False
        result["error"] = "Data is empty"
        log_and_print(result, debug)
        return result

    part = " AND ".join([f"{key}=?" for key in data.keys()])
    values = list(data.values())

    query = f'SELECT * FROM {table} WHERE {part}'
    try:

        with sqlite3.connect(file) as db:
            cursor = db.cursor()
            cursor.execute(query, values)
            result["data"] = cursor.fetchall() if all else cursor.fetchone()
    
    except Exception as error:
        result["sucsess"] = False
        result["error"] = error

    log_and_print(result, debug)
    return result


def sql_sget(file, table, data, all=False, check=False, debug=False):
    result = {"process": "#sql_sget", "sucsess": True, "error": None, "data": None}

    if not data:
        result["sucsess"] = False
        result["error"] = "Data is empty"
        log_and_print(result, debug)
        return result

    try:

        tmp = sql_get(file, table, data, all)
        result["error"] = tmp["error"]
        result["data"] = tmp["data"]

        if result["data"] is not None and len(result["data"]) != 0:
            return result

        if check:
            save_result = sql_save(file, table, data)
            if save_result["sucsess"]:
                tmp = sql_get(file, table, data, all)
                result["error"] = tmp["error"]
                result["data"] = tmp["data"]
            else:
                result["sucsess"] = False
                result["error"] = save_result["error"]

    except Exception as error:
        result["sucsess"] = False
        result["error"] = error

    log_and_print(result, debug)
    return result


def sql_update(file, table, data, debug=False):
    result = {"process": "#sql_update", "sucsess": True, "error": None, "data": None}

    values = list(data.values())
    columns = "=?, ".join(data.keys()) + "=?"

    query = f"UPDATE {table} SET {columns}"
    
    if not data:
        result["sucsess"] = False
        result["error"] = "Data is empty"
        log_and_print(result, debug)
        return result
    try:

        with sqlite3.connect(file) as db:
            cursor = db.cursor()
            cursor.execute(query, values)
            db.commit()
            result["data"] = sql_get(file, table, {"userid": data["userid"]})["data"]

    except Exception as error:
        result["sucsess"] = False
        result["error"] = error

    log_and_print(result, debug)
    return result

def get_all_items(debug=False):
    result = {"process": "#get_all_items", "sucsess": True, "error": None, "data": None}

    query = 'SELECT smalname FROM items'

    try:

        with sqlite3.connect('main_base\\items.db') as db:
            cursor = db.cursor()
            cursor.execute(query)
            result["data"] = cursor.fetchall()

    except Exception as error:
        result["sucsess"] = False
        result["error"] = error

    log_and_print(result, debug)
    return result