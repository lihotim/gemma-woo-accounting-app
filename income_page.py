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
def fetch_all_incomes_cached():
    return db.fetch_all_incomes()

def add_income_item(date, category, item, customer, amount):
    current_time = datetime.now().strftime("%H:%M:%S")
    full_datetime = f"{date.strftime('%Y-%m-%d')}-{current_time}"
    async def add_income_item_async(full_datetime, category, item, customer, amount):
        db.insert_income(full_datetime, category, item, customer, amount)
        st.cache_data.clear()
    coro = add_income_item_async(full_datetime, category, item, customer, amount)
    with st.spinner("Adding income data..."):
        asyncio.run(coro)
    st.success("Success! Now refresh page...")
    time.sleep(1)
    st.experimental_rerun()

def remove_income(income_id):
    async def remove_income_async(income_id):
        db.delete_income(income_id)
        st.cache_data.clear()
    coro = remove_income_async(income_id)
    with st.spinner("Removing income data..."):
        asyncio.run(coro)
    st.success("Success! Now refresh page...")
    time.sleep(1)
    st.experimental_rerun()


def income():
    # Add income form
    st.header("Add Income")
    CATEGORIES = ccconfig.INCOME_CATEGORIES # ["Consultation", "Herb Sale", "Class", "Others"]
    COLUMN_ORDER = ccconfig.INCOME_COLUMN_ORDER # ["key", "category", "item", "customer", "amount"]
    date = st.date_input("Date")
    category = st.selectbox("Category", CATEGORIES)
    item = st.text_input("Item")
    customer = st.text_input("Customer name")
    amount = st.number_input("Amount", step=1, min_value=0)
    if st.button("Add New Income Item"):
        if any(field == "" for field in [date, category, item, customer, amount]):
            st.warning("Please fill in all the required fields.")
        else:
            add_income_item(date, category, item, customer, amount)


    st.divider()
    income_data = fetch_all_incomes_cached()
    df_income = pd.DataFrame(income_data)
    df_income = df_income[COLUMN_ORDER] # rearrange column order
    df_income['month'] = df_income['key'].apply(utils.format_month) # add a new column "month", by reading the date from "key"
    month_options = df_income['month'].unique() # list of months, e.g. ['2023 May' '2023 Jun' '2023 Jul' '2023 Aug']


    # Display all incomes and delete button in 2 columns (2:1)
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Income Items")

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
        filtered_df_income = df_income[
            (df_income['category'].isin(selected_categories)) &
            (df_income['month'].isin(selected_month))
        ]
        filtered_df_income = filtered_df_income.drop(columns=['month'])  # Drop the 'month' column
        st.dataframe(filtered_df_income, 
                     hide_index=True, 
                     use_container_width=True,
                     column_config={
                        "key": st.column_config.Column("Income ID", disabled=True, help="Info: Not editable"),
                        "category": st.column_config.TextColumn("Category"),
                        "item": st.column_config.TextColumn("Item"),
                        "customer": st.column_config.TextColumn("Customer"),
                        "amount": st.column_config.NumberColumn("Amount", format="$%d"),
                     }
        )

    with col2:
        st.subheader("Remove an income item:")
        income_id_list = df_income["key"].tolist()
        chosen_income_id = st.text_input("Input Income ID to remove it:")
        with st.expander("Confirm delete income item", expanded=False):
            delete_button = st.button("Confirm", type="primary")

        if delete_button:
            if chosen_income_id:
                if chosen_income_id in income_id_list:
                    remove_income(chosen_income_id)
                    st.success(f"Deleted income with id: {chosen_income_id}, please refresh the page.")
                else:
                    st.warning("Selected income id does not exist.")
            else:
                st.warning("Please select an income id to delete.")


    # Show pie chart and table in 2 columns
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Income Distribution")
        income_by_category = filtered_df_income.groupby("category")["amount"].sum()
        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            income_by_category,
            labels=[f"{label} (${value:.2f})" for label, value in income_by_category.items()],
            autopct="%1.1f%%",
        )
        ax.set_title(f"Income by Category")
        plt.setp(autotexts, size=10, weight="bold")
        st.pyplot(fig)

    with col2:
        total_income = income_by_category.sum()
        selected_month_str = ", ".join(selected_month)
        st.subheader("Total Income")
        st.write(f"Period: {selected_month_str}")

        income_table = pd.DataFrame(income_by_category)
        income_table = income_table.sort_values(by="amount", ascending=False)
        st.dataframe(
            income_table, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "category": st.column_config.TextColumn("Category"),
                "amount": st.column_config.NumberColumn("Amount", format="$%d")
                }
        )
        st.metric(label="HKD", value=f"${total_income:.2f}")

        # Display counts for certain categories
        for category in ccconfig.CATEGORIES_TO_COUNT: # ["Consultation", "Herb Sale"]
            category_count = filtered_df_income[filtered_df_income['category'] == category].shape[0]
            st.metric(label=f"{category} Count", value=category_count)


if __name__ == "__main__":
    income()