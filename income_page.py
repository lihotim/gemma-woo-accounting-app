import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import database as db

# feature we want to add: try to use st.data_editor to manage update, delete (on_change)

@st.cache_data
def fetch_all_incomes_cached():
    return db.fetch_all_incomes()


def income():
    st.header("Add Income")
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Consultation", "Herb sale", "Class", "Others"])
    item = st.text_input("Item")
    customer = st.text_input("Customer")
    amount = st.number_input("Amount", step=1, min_value=0)
    
    if st.button("Add new Income item"):
        current_time = datetime.now().strftime("%H:%M:%S")
        full_datetime = f"{date.strftime('%Y-%m-%d')}-{current_time}"
        print(f"key: {full_datetime}, Category: {category}, Item: {item}, Customer: {customer}, Amount: {amount}")
        db.insert_income(full_datetime, category, item, customer, amount)
        st.cache_data.clear()
        st.success("Income item has been added.")


    # Show all incomes
    st.divider()
    st.subheader("All Incomes")
    column_order = ["key", "category", "item", "customer", "amount"]
    income_data = fetch_all_incomes_cached()
    df = pd.DataFrame(income_data)
    df = df[column_order]
    df = df.rename(columns={"key": "Date", "category": "Category", "item": "Item", "customer": "Customer", "amount": "Amount"}) 
    st.dataframe(df, hide_index=True)


    # Show pie chart and table in 2 columns
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Incomes by Category Chart")
        income_by_category = df.groupby("Category")["Amount"].sum()
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
        st.subheader("Incomes by Category Table")
        income_table = pd.DataFrame(income_by_category).reset_index()
        income_table.columns = ["Category", "Amount"]
        income_table = income_table.sort_values(by="Amount", ascending=False)
        st.dataframe(income_table, hide_index=True)


    # Calculate and display total income
    st.divider()
    total_income = income_by_category.sum()
    st.subheader("Total Income")
    st.metric(label = "Income", value = f"${total_income:.2f}")

if __name__ == "__main__":
    income()