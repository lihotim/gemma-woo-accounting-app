import streamlit as st
from streamlit_option_menu import option_menu

# pages
from inventory_page import inventory
from income_page import income
from expense_page import expense
from statistics_page import statistics

OPTIONS = ["Inventory", "Income", "Expense", "Statistics"]


def streamlit_menu():
    # 2. horizontal menu w/o custom style
    selected = option_menu(
        menu_title="Gemma Woo's Accounting app",  # required
        options=OPTIONS,  # required
        # icons=["house", "book", "envelope"],  # optional
        # menu_icon="cast",  # optional
        default_index=0,  # optional
        orientation="horizontal",
    )
    return selected


selected = streamlit_menu()

if selected == OPTIONS[0]:
    # st.title(f"{selected}")
    inventory()
if selected == OPTIONS[1]:
    # st.title(f"{selected}")
    income()
if selected == OPTIONS[2]:
    # st.title(f"{selected}")
    expense()
if selected == OPTIONS[3]:
    # st.title(f"{selected}")
    statistics()
