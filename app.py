import streamlit as st
from streamlit_option_menu import option_menu

# pages
from inventory_page import inventory
from income_page import income
from expense_page import expense
from statistics_page import statistics

# features we want:
# - For "Inventory" page, should add "+", "-" buttons to update the inventory more easily
# - update incomes and expenses using st.editor
# - sort incomes and expenses by month or season (st.multiselect), e.g. only showing Aug or Jun-Aug
# - In "Statistics" page, may show metrics in delta, e.g. change in income/expense compared with last month
# - Export charts or diagrams in jpg, doc, csv...
# - check: for st.editor, can we insert a new row directly?

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
