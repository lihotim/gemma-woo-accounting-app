import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date

def generate_sample_income_data():
    categories = ["Consultation", "Herb sale", "Class", "Other"]
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 8, 31)

    data = []
    for _ in range(10):
        date = generate_random_date(start_date, end_date)
        item = f"Item{_ + 1}"
        category = random.choice(categories)
        amount = random.randint(50, 500)
        data.append({"Date": date, "Item": item, "Category": category, "Amount": amount})

    return data

def generate_sample_expense_data():
    categories = ["Rent", "Salaries", "Supplies", "Utilities", "Advertising", "Travel", "Other"]
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 8, 31)

    data = []
    for _ in range(10):
        date = generate_random_date(start_date, end_date)
        item = f"Item{_ + 1}"
        category = random.choice(categories)
        amount = random.randint(50, 500)
        data.append({"Date": date, "Item": item, "Category": category, "Amount": amount})

    return data


def statistics():
    st.header("Statistics")
    
    sample_income_data = generate_sample_income_data()
    df_income = pd.DataFrame(sample_income_data)
    

    sample_expense_data = generate_sample_expense_data()
    df_expense = pd.DataFrame(sample_expense_data)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Income")
        st.dataframe(df_income)

        # Create a pie chart to show incomes by category
        income_by_category = df_income.groupby("Category")["Amount"].sum()
        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            income_by_category,
            labels=[f"{label} (${value:.2f})" for label, value in income_by_category.items()],
            autopct="%1.1f%%",
        )
        ax.set_title("Income by Category")
        plt.setp(autotexts, size=10, weight="bold")
        st.pyplot(fig)

        # Display income by category in a table
        expense_table = pd.DataFrame(income_by_category).reset_index()
        expense_table.columns = ["Category", "Amount"]
        st.table(expense_table)

        
    with col2:
        st.subheader("Expense")
        st.dataframe(df_expense)
        # Create a pie chart to show expenses by category
        expense_by_category = df_expense.groupby("Category")["Amount"].sum()
        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            expense_by_category,
            labels=[f"{label} (${value:.2f})" for label, value in expense_by_category.items()],
            autopct="%1.1f%%",
        )
        ax.set_title("Expense by Category")
        plt.setp(autotexts, size=10, weight="bold")
        st.pyplot(fig)

        # Display income by category in a table
        expense_table = pd.DataFrame(expense_by_category).reset_index()
        expense_table.columns = ["Category", "Amount"]
        st.table(expense_table)

    total_income = income_by_category.sum()
    total_expense = expense_by_category.sum()
    st.metric(label = "Total Income", value = f"{total_income:.2f}")
    st.metric(label = "Total Expense", value = f"{total_expense:.2f}")


if __name__ == "__main__":
    statistics()