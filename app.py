import streamlit as st
import streamlit_authenticator as stauth
from streamlit_option_menu import option_menu
from pathlib import Path

import database as db


# pages
from inventory_page import inventory
from income_page import income
from expense_page import expense
from statistics_page import statistics

# features we want:
# - change ALL fetch_all functions to async (need?)

PAGE_TITLE = "鎧碇有限公司 - 會計程式"
TAB_OPTIONS = ["存貨", "收入", "支出", "統計"]
    
# --- PATH SETTINGS ---
THIS_DIR = Path(__file__).parent if "__file__" in locals() else Path.cwd()
ASSETS_DIR = THIS_DIR / "assets"
STYLES_DIR = THIS_DIR / "styles"
CSS_FILE = STYLES_DIR / "main.css"

def load_css_file(css_file_path):
    with open(css_file_path) as f:
        return st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- PAGE CONFIG ---
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed",
)
load_css_file(CSS_FILE)


def streamlit_menu():
    # horizontal menu w/o custom style
    selected = option_menu(
        menu_icon="clipboard-data-fill",  # optional, from "https://icons.getbootstrap.com/"
        menu_title=PAGE_TITLE,  # required
        options=TAB_OPTIONS,  # required
        icons=["inboxes-fill", "cash-stack", "cash-stack", "graph-up"],  # optional, from "https://icons.getbootstrap.com/"
        default_index=0,  # optional
        orientation="horizontal",
    )
    return selected

selected = streamlit_menu()

# --- USER AUTHENTICATION ---
users = db.fetch_all_users()

usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "sales_dashboard", "abcdef", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("請先登入：", "sidebar")

if authentication_status == False:
    st.error("用戶名稱或密碼不正確。")

if authentication_status == None:
    st.warning("請輸入用戶名稱及密碼。")

if authentication_status:
    st.sidebar.title(f"歡迎您，{name}！")
    authenticator.logout("登出", "sidebar")

    if selected == TAB_OPTIONS[0]:
        inventory()
    if selected == TAB_OPTIONS[1]:
        income()
    if selected == TAB_OPTIONS[2]:
        expense()
    if selected == TAB_OPTIONS[3]:
        statistics()
