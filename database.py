import os

from deta import Deta  # pip install deta
from dotenv import load_dotenv  # pip install python-dotenv


# Load the environment variables
load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")

# Initialize with a project key
deta = Deta(DETA_KEY)

# This is how to create/connect a database
inventory_db = deta.Base("inventory_db")
income_db = deta.Base("income_db")
expense_db = deta.Base("expense_db")


# ---- 1. inventory_db ----

def insert_herb(herb_id, brand, herb_name, unit_price, inventory):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return inventory_db.put(
        {
            "key": herb_id,
            "brand": brand,
            "herb_name": herb_name,
            "unit_price": unit_price,
            "inventory": inventory,
        }
    )


# print(insert_herb("herb03", "HoiTin", "Hoi Tin A", 300, 3))


def fetch_all_herbs():
    """Returns a dict of all users"""
    res = inventory_db.fetch()
    return res.items

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

def insert_income(time, category, item, customer, amount):
    """Returns the item on a successful income creation, otherwise raises and error"""
    return income_db.put(
        {
            "key": time,
            "category": category,
            "item": item,
            "customer": customer,
            "amount": amount,
        }
    )


# print(insert_income("2023-08-16-08:10", "Consultation", "Tim", "Covid", 100))


def fetch_all_incomes():
    """Returns a dict of all incomes"""
    res = income_db.fetch()
    return res.items

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

def insert_expense(time, category, item, amount):
    """Returns the item on a successful income creation, otherwise raises and error"""
    return expense_db.put(
        {
            "key": time,
            "category": category,
            "item": item,
            "amount": amount,
        }
    )


# print(insert_expense("2023-08-16-09:09", "Utilities", "Electricities of August", 100))


def fetch_all_expenses():
    """Returns a dict of all expenses"""
    res = expense_db.fetch()
    return res.items

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