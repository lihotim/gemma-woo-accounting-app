import os
import random

from deta import Deta  # pip install deta
from dotenv import load_dotenv  # pip install python-dotenv
import columns_categories_config as ccconfig

# Load the environment variables
load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")

# Initialize with a project key
deta = Deta(DETA_KEY)

# This is how to create/connect a database
inventory_db = deta.Base("inventory_db")
income_db = deta.Base("income_db")
expense_db = deta.Base("expense_db")
users_db = deta.Base("users_db")


# ---- 1. inventory_db ----

def insert_herb(herb_id, brand, herb_name, cost_price, selling_price, inventory):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return inventory_db.put(
        {
            "key": herb_id,
            "brand": brand,
            "herb_name": herb_name,
            "cost_price": cost_price,
            "selling_price": selling_price,
            "inventory": inventory,
        }
    )

# Insert 1 herb manually
# print(insert_herb("h1", "三九", "herb-1001", 100, 200, 10))

# Insert many herbs
brand_list = ccconfig.HERB_BRANDS
chinese_herbs = [
    "人蔘", "黃芪", "陳皮", "白芍", "當歸",
    "甘草", "桂枝", "川芎", "熟地黃", "五味子",
    "黃連", "枸杞子", "柴胡", "茯苓", "麥門冬",
    "防風", "金櫻子", "白朮", "艾葉", "連翹",
    "川貝", "山藥", "田七", "玄參", "阿膠",
    "山茱萸", "蒲公英", "槐花", "玉竹", "天麻"
]
# for id in range(1, 31): # loop from 1 to 30
#     brand = random.choice(brand_list)
#     herb_name = random.choice(chinese_herbs)
#     result = insert_herb(f"h0{id}", brand, herb_name, 100, 200, 10)
#     print(result)



def fetch_all_herbs():
    """Returns a dict of all herbs"""
    all_herbs = []
    last_item_key = None
    while True:
        response = inventory_db.fetch(limit=100, last=last_item_key)
        # print(len(response.items))
        all_herbs.extend(response.items)
        if not response.last:
            break
        last_item_key = response.last
    return all_herbs

# print(fetch_all_herbs())



def get_herb(herb_id):
    """If not found, the function will return None"""
    return inventory_db.get(herb_id)

# print(get_herb("h13"))


def update_herb(herb_id, updates):
    """If the item is updated, returns None. Otherwise, an exception is raised"""
    # updates = {
    #     "unit_price":new_unit_price,
    #     "inventory":new_inventory,
    # }
    return inventory_db.update(updates, herb_id)

# print(update_herb("h01", {"inventory":99}))


def delete_herb(herb_id):
    """Always returns None, even if the key does not exist"""
    return inventory_db.delete(herb_id)

# print(delete_herb("h14"))



# ---- 2. income_db ----

def insert_income(income_id, date, category, item, customer, amount):
    """Returns the item on a successful income creation, otherwise raises and error"""
    return income_db.put(
        {
            "key": income_id,
            "date": date,
            "category": category,
            "item": item,
            "customer": customer,
            "amount": amount,
        }
    )


# print(insert_income("C00036", "28-Aug-23", "診症", "Tim", "///", 111))


def fetch_all_incomes():
    """Returns a dict of all incomes"""
    all_incomes = []
    last_item_key = None
    while True:
        response = income_db.fetch(limit=100, last=last_item_key)
        all_incomes.extend(response.items)
        if not response.last:
            break
        last_item_key = response.last
    return all_incomes

# print(fetch_all_incomes())


def get_income(time):
    """If not found, the function will return None"""
    return income_db.get(time)

# print(get_income("2023-08-16-08:00"))


def update_income(time, updates):
    """If the item is updated, returns None. Otherwise, an exception is raised"""
    # updates = {}
    return income_db.update(updates, time)

# print(update_income("2023-08-16-08:02:00", {"amount": 195}))


def delete_income(time):
    """Always returns None, even if the key does not exist"""
    return income_db.delete(time)

# print(delete_income("2023-08-16-08:00"))


# ---- 3. expense_db ----

def insert_expense(expense_id, date, category, item, amount):
    """Returns the item on a successful income creation, otherwise raises and error"""
    return expense_db.put(
        {
            "key": expense_id,
            "date": date,
            "category": category,
            "item": item,
            "amount": amount,
        }
    )


# print(insert_expense("2023-08-16-09:09", "Utilities", "Electricities of August", 100))


def fetch_all_expenses():
    """Returns a dict of all expenses"""
    all_expenses = []
    last_item_key = None
    while True:
        response = expense_db.fetch(limit=100, last=last_item_key)
        all_expenses.extend(response.items)
        if not response.last:
            break
        last_item_key = response.last
    return all_expenses

# print(fetch_all_expenses())


def get_expense(time):
    """If not found, the function will return None"""
    return expense_db.get(time)

# print(get_expense("2023-08-16-08:04"))


def update_expense(time, updates):
    """If the item is updated, returns None. Otherwise, an exception is raised"""
    # updates = {}
    return expense_db.update(updates, time)

# print(update_expense("2023-08-16-08:03", {"amount":199}))


def delete_expense(time):
    """Always returns None, even if the key does not exist"""
    return expense_db.delete(time)

# print(delete_expense("2023-08-16-08:02"))


# ---- 4. users_db ----
def insert_user(username, name, password):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return users_db.put({"key": username, "name": name, "password": password})


def fetch_all_users():
    """Returns a dict of all users"""
    res = users_db.fetch()
    return res.items


def get_user(username):
    """If not found, the function will return None"""
    return users_db.get(username)


def update_user(username, updates):
    """If the item is updated, returns None. Otherwise, an exception is raised"""
    return users_db.update(updates, username)


def delete_user(username):
    """Always returns None, even if the key does not exist"""
    return users_db.delete(username)