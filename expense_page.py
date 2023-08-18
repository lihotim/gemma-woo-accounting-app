import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import asyncio
from datetime import datetime
import utils
import time

import database as db
import columns_categories_config as ccconfig

@st.cache_data
def fetch_all_expenses_cached():
    return db.fetch_all_expenses()

def add_expense_item(date, category, item, amount):
    current_time = datetime.now().strftime("%H:%M:%S")
    full_datetime = f"{date.strftime('%Y-%m-%d')}-{current_time}"
    async def add_expense_item_async(full_datetime, category, item, amount):
        db.insert_expense(full_datetime, category, item, amount)
        st.cache_data.clear()
    coro = add_expense_item_async(full_datetime, category, item, amount)
    with st.spinner("Adding expense data..."):
        asyncio.run(coro)
    st.success("Success! Now refresh page...")
    time.sleep(1)
    st.experimental_rerun()
    
def remove_expense(expense_id):
    async def remove_expense_async(expense_id):
        db.delete_expense(expense_id)
        st.cache_data.clear()
    coro = remove_expense_async(expense_id)
    with st.spinner("Removing expense data..."):
        asyncio.run(coro)
    st.success("Success! Now refresh page...")
    time.sleep(1)
    st.experimental_rerun()


def expense():
    # Add expense form
    st.header("Add Expense")
    CATEGORIES = ccconfig.EXPENSE_CATEGORIES # ["Rent", "Salaries", "Utilities", "Advertising", "Travel", "Others"]
    COLUMN_ORDER = ccconfig.EXPENSE_COLUMN_ORDER # ["key", "category", "item", "amount"] 
    date = st.date_input("Date")
    category = st.selectbox("Category", CATEGORIES)
    item = st.text_input("Item")
    amount = st.number_input("Amount", step=1, min_value=0)
    if st.button("Add New Expense Item"):
        if any(field == "" for field in [date, category, item, amount]):
            st.warning("Please fill in all the required fields.")
        else:
            add_expense_item(date, category, item, amount)



    st.divider()
    expense_data = fetch_all_expenses_cached()
    df_expense = pd.DataFrame(expense_data)
    df_expense = df_expense[COLUMN_ORDER] # rearrange column order
    df_expense['month'] = df_expense['key'].apply(utils.format_month) # add a new column "month", by reading the date from "key"
    month_options = df_expense['month'].unique() # list of months, e.g. ['2023 May' '2023 Jun' '2023 Jul' '2023 Aug']
    
     
    # Display all expenses and delete button in 2 columns (2:1)
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Expense Items")

        # Filter by month and category
        selected_month = st.multiselect(
                'Filter by Month',
                options=month_options,
                default=month_options[-1], # default to choose only the latest month
        )
        selected_categories = st.multiselect(
            'Filter by Category',
            options=CATEGORIES,
            default=CATEGORIES,
        )
        filtered_df_expense = df_expense[
            (df_expense['category'].isin(selected_categories)) &
            (df_expense['month'].isin(selected_month))
        ]
        filtered_df_expense = filtered_df_expense.drop(columns=['month'])  # Drop the 'month' column
        st.dataframe(filtered_df_expense, 
                     hide_index=True, 
                     use_container_width=True,
                     column_config={
                        "key": st.column_config.Column("Expense ID", disabled=True, help="Info: Not editable"),
                        "category": st.column_config.TextColumn("Category"),
                        "item": st.column_config.TextColumn("Item"),
                        "amount": st.column_config.NumberColumn("Amount", format="$%d"),
                     }
        )


    with col2:
        st.subheader("Remove an expense item:")
        expense_id_list = df_expense["key"].tolist()
        chosen_expense_id = st.text_input("Input Expense ID to remove it:")
        with st.expander("Confirm delete expense item", expanded=False):
            delete_button = st.button("Confirm", type="primary")

        if delete_button:
            if chosen_expense_id:
                if chosen_expense_id in expense_id_list:
                    remove_expense(chosen_expense_id)
                    st.success(f"Deleted expense with id: {chosen_expense_id}, please refresh the page.")
                else:
                    st.warning("Selected expense id does not exist.")
            else:
                st.warning("Please select an expense id to delete.")





    # Show pie chart and table in 2 columns
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Expense Distribution")
        expense_by_category = filtered_df_expense.groupby("category")["amount"].sum()
        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            expense_by_category,
            labels=[f"{label} (${value:.2f})" for label, value in expense_by_category.items()],
            autopct="%1.1f%%",
        )
        ax.set_title(f"Expense by Category")
        plt.setp(autotexts, size=10, weight="bold")
        st.pyplot(fig)

    with col2:
        total_expense = expense_by_category.sum()
        selected_month_str = ", ".join(selected_month)
        st.subheader("Total Expense")
        st.write(f"Period: {selected_month_str}")

        expense_table = pd.DataFrame(expense_by_category)
        expense_table = expense_table.sort_values(by="amount", ascending=False)
        st.dataframe(
            expense_table, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "category": st.column_config.TextColumn("Category"),
                "amount": st.column_config.NumberColumn("Amount", format="$%d")
                }
        )
        st.metric(label="HKD", value=f"${total_expense:.2f}")


if __name__ == "__main__":
    expense()