import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import database as db

# feature we want to add: try to use st.data_editor to manage update, delete (on_change)

@st.cache_data
def fetch_all_expenses_cached():
    return db.fetch_all_expenses()


def expense():
    st.header("Expense")
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Rent", "Salaries", "Supplies", "Utilities", "Advertising", "Travel", "Other"])
    item = st.text_input("Item")
    amount = st.number_input("Amount", step=1, min_value=0)
    
    if st.button("Add new Expense item"):
        current_time = datetime.now().strftime("%H:%M:%S")
        full_datetime = f"{date.strftime('%Y-%m-%d')}-{current_time}"
        print(f"Key: {full_datetime}, Category: {category}, Item: {item}, Amount: {amount}")
        db.insert_expense(full_datetime, category, item, amount)
        st.cache_data.clear()
        st.success("Expense item has been added.")


    # Show all expenses
    st.divider()
    st.subheader("All Expenses")
    column_order = ["key", "category", "item", "amount"]
    expense_data = fetch_all_expenses_cached()
    df = pd.DataFrame(expense_data)
    df = df[column_order]
    df = df.rename(columns={"key": "Date", "category": "Category", "item": "Item", "amount": "Amount"}) 
    st.dataframe(df, hide_index=True)


    # Show pie chart and table in 2 columns
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Expense by Category (Chart)")
        expense_by_category = df.groupby("Category")["Amount"].sum()
        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            expense_by_category,
            labels=[f"{label} (${value:.2f})" for label, value in expense_by_category.items()],
            autopct="%1.1f%%",
        )
        ax.set_title("Expenses by Category (Table)")
        plt.setp(autotexts, size=10, weight="bold")
        st.pyplot(fig)

    with col2:
        st.subheader("Expenses by Category (Table)")
        expense_table = pd.DataFrame(expense_by_category).reset_index()
        expense_table.columns = ["Category", "Amount"]
        expense_table = expense_table.sort_values(by="Amount", ascending=False)
        st.dataframe(expense_table, hide_index=True)


    # Calculate and display total expense
    st.divider()
    total_expense = expense_by_category.sum()
    st.subheader("Total Expense")
    st.metric(label = "Expense", value = f"{total_expense:.2f}")

if __name__ == "__main__":
    expense()