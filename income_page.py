import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import database as db
import asyncio

# feature we want to add:
# - may change "key" to another format, then add a "date" column
# - for pie charts, table by category and metrics, allow st.multiselect to choose months
# - may filter by month, category, customer, or even values >$1000 (?)  

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
    st.experimental_rerun()


def remove_income(income_id):
    async def remove_income_async(income_id):
        db.delete_income(income_id)
        st.cache_data.clear()
    coro = remove_income_async(income_id)
    with st.spinner("Removing income data..."):
        asyncio.run(coro)
    st.experimental_rerun()


def income():
    st.header("Add Income")
    CATEGORIES = ["Consultation", "Herb sale", "Class", "Others"]
    COLUMN_ORDER = ["key", "category", "item", "customer", "amount"]
    date = st.date_input("Date")
    category = st.selectbox("Category", CATEGORIES)
    item = st.text_input("Item")
    customer = st.text_input("Customer")
    amount = st.number_input("Amount", step=1, min_value=0)
    if st.button("Add New Income item"):
        add_income_item(date, category, item, customer, amount)


    st.divider()

    selected_month = st.multiselect(
        'Filter by Month',
        options=["2023 Jun", "2023 Jul", "2023 Aug"],
        default=["2023 Jun", "2023 Jul", "2023 Aug"],
    )
    selected_categories = st.multiselect(
        'Filter by Category',
        options=CATEGORIES,
        default=CATEGORIES,
    )

    # st.write('You selected:', selected_categories)
    # print('You selected:', selected_categories)

    # Display all incomes and delete button in 2 columns (2:1)
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("All Incomes")
        income_data = fetch_all_incomes_cached()
        df_income = pd.DataFrame(income_data)
        df_income = df_income[COLUMN_ORDER]
        filtered_df_income = df_income[df_income['category'].isin(selected_categories)]
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
    st.divider()
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Incomes Pie Chart")
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
        st.subheader("Incomes by Category")
        income_table = pd.DataFrame(income_by_category).reset_index()
        income_table.columns = ["Category", "Amount"]
        income_table = income_table.sort_values(by="Amount", ascending=False)
        st.dataframe(income_table, hide_index=True, use_container_width=True)


    # Calculate and display total income
    st.divider()
    total_income = income_by_category.sum()
    st.subheader("Total Income")
    st.metric(label = "Income", value = f"${total_income:.2f}")

if __name__ == "__main__":
    income()