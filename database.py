import os

from deta import Deta  # pip install deta
from dotenv import load_dotenv  # pip install python-dotenv


# Load the environment variables
load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")

# Initialize with a project key
deta = Deta(DETA_KEY)

# This is how to create/connect a database
db = deta.Base("inventory_db")


def insert_herb(herb_id, brand, herb_name, unit_price, inventory):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return db.put(
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
    res = db.fetch()
    return res.items


# print(fetch_all_herbs())


def get_herb(username):
    """If not found, the function will return None"""
    return db.get(username)


def update_herb(username, updates):
    """If the item is updated, returns None. Otherwise, an exception is raised"""
    return db.update(updates, username)


def delete_herb(username):
    """Always returns None, even if the key does not exist"""
    return db.delete(username)
