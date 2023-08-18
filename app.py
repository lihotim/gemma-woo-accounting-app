import streamlit as st
from streamlit_option_menu import option_menu
from pathlib import Path

# pages
from inventory_page import inventory
from income_page import income
from expense_page import expense
from statistics_page import statistics

# features we want:
# - fix ALL the titles, headers, labels, copywritings
# - change ALL fetch_all functions to async, for all pages (need?)
# - test if data length exceeds 1000


TAB_OPTIONS = ["Inventory", "Income", "Expense", "Statistics"]
    
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
    page_title="Gemma Woo's Accounting App",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed",
)
load_css_file(CSS_FILE)

def streamlit_menu():
    # 2. horizontal menu w/o custom style
    selected = option_menu(
        menu_title="Gemma Woo's Accounting app",  # required
        options=TAB_OPTIONS,  # required
        # icons=["house", "book", "envelope"],  # optional
        # menu_icon="cast",  # optional
        default_index=0,  # optional
        orientation="horizontal",
    )
    return selected

selected = streamlit_menu()

if selected == TAB_OPTIONS[0]:
    # st.title(f"{selected}")
    inventory()
if selected == TAB_OPTIONS[1]:
    # st.title(f"{selected}")
    income()
if selected == TAB_OPTIONS[2]:
    # st.title(f"{selected}")
    expense()
if selected == TAB_OPTIONS[3]:
    # st.title(f"{selected}")
    statistics()
