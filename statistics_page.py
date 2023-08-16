import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import database as db

# features we want:
# - change ALL fetch_all functions to async, for all pages (need?)
# - display historical incomes and expenses using line charts (1 line for income, 1 line for expense)
# - can also apply category filter

# - may display metrics: compare income & expense this month and last month, then show delta (%)
# - export graph as jpg, other data + graph as excel (or maybe word)
# - 

@st.cache_data
def fetch_all_incomes_cached():
    return db.fetch_all_incomes()
@st.cache_data
def fetch_all_expenses_cached():
    return db.fetch_all_expenses()


def statistics():
    st.header("Statistics")
    
   

# --------------------

    income_data = fetch_all_incomes_cached()
    df_income = pd.DataFrame(income_data)
    
    expense_data = fetch_all_expenses_cached()
    df_expense = pd.DataFrame(expense_data)

    # Display incomes and expenses by category in pie charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Incomes")
        # st.dataframe(df_income)

        income_by_category = df_income.groupby("category")["amount"].sum()
        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            income_by_category,
            labels=[f"{label} (${value:.2f})" for label, value in income_by_category.items()],
            autopct="%1.1f%%",
        )
        ax.set_title("Incomes by Category")
        plt.setp(autotexts, size=10, weight="bold")
        st.pyplot(fig)

    with col2:
        st.subheader("Expenses")
        # st.dataframe(df_expense)

        expense_by_category = df_expense.groupby("category")["amount"].sum()
        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            expense_by_category,
            labels=[f"{label} (${value:.2f})" for label, value in expense_by_category.items()],
            autopct="%1.1f%%",
        )
        ax.set_title("Expenses by Category")
        plt.setp(autotexts, size=10, weight="bold")
        st.pyplot(fig)

        
    # Display incomes and expenses by category in tables
    col1, col2 = st.columns(2)
    with col1:
        income_table = pd.DataFrame(income_by_category).reset_index()
        income_table.columns = ["Category", "Amount"]
        income_table = income_table.sort_values(by="Amount", ascending=False)
        st.dataframe(income_table, hide_index=True, use_container_width=True)
    with col2:
        expense_table = pd.DataFrame(expense_by_category).reset_index()
        expense_table.columns = ["Category", "Amount"]
        expense_table = expense_table.sort_values(by="Amount", ascending=False)
        st.dataframe(expense_table, hide_index=True, use_container_width=True)


    # Metrics
    col1, col2, col3 = st.columns(3)
    total_income = income_by_category.sum()
    total_expense = expense_by_category.sum()
    col1.metric(label = "Total Income", value = f"{total_income:.2f}")
    col2.metric(label = "Total Expense", value = f"{total_expense:.2f}")
    col3.metric(label = "???", value = f"{0.00}")


if __name__ == "__main__":
    statistics()