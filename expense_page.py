import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import asyncio
from datetime import datetime
import utils
import time

import database as db
import columns_categories_config as ccconfig

@st.cache_data
def fetch_all_expenses_cached():
    data = db.fetch_all_expenses()
    return data

def add_expense_item(date, category, item, amount):
    current_time = datetime.now().strftime("%H:%M:%S")
    full_datetime = f"{date.strftime('%Y-%m-%d')}-{current_time}"
    async def add_expense_item_async(full_datetime, category, item, amount):
        db.insert_expense(full_datetime, category, item, amount)
        st.cache_data.clear()
    coro = add_expense_item_async(full_datetime, category, item, amount)
    with st.spinner("正在加入支出數據..."):
        asyncio.run(coro)
    st.success(ccconfig.SUCCESS_MSG)
    time.sleep(1)
    st.experimental_rerun()
    
def remove_expense(expense_id):
    async def remove_expense_async(expense_id):
        db.delete_expense(expense_id)
        st.cache_data.clear()
    coro = remove_expense_async(expense_id)
    with st.spinner("正在移除支出數據..."):
        asyncio.run(coro)
    st.success(ccconfig.SUCCESS_MSG)
    time.sleep(1)
    st.experimental_rerun()


def expense():
    # Add expense form
    st.header("新增支出")
    CATEGORIES = ccconfig.EXPENSE_CATEGORIES # ["Rent", "Salaries", "Utilities", "Advertising", "Travel", "Others"]
    COLUMN_ORDER = ccconfig.EXPENSE_COLUMN_ORDER # ["key", "category", "item", "amount"] 
    date = st.date_input("日期")
    category = st.selectbox("類別", CATEGORIES)
    item = st.text_input("項目")
    amount = st.number_input("金額", step=1, min_value=0)
    if st.button("新增支出項目"):
        if any(field == "" for field in [date, category, item, amount]):
            st.warning(ccconfig.WARNING_MSG_FILL_ALL)
        else:
            add_expense_item(date, category, item, amount)



    st.divider()
    expense_data = fetch_all_expenses_cached()
    df_expense = pd.DataFrame(expense_data, columns=COLUMN_ORDER) # initialize dataframe with the expected column order
    df_expense['month'] = df_expense['key'].apply(utils.format_month) # add a new column "month", by reading the date from "key"
    month_options = df_expense['month'].unique() # list of months, e.g. ['2023 May' '2023 Jun' '2023 Jul' '2023 Aug']
    
     
    # Display all expenses and delete button in 2 columns (2:1)
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("支出項目：")

        # Filter by month and category
        selected_month = st.multiselect(
            "按月份篩選",
            options=month_options,
            default=month_options[-1] if len(month_options) > 0 else month_options, # default to choose only the latest month
        )
        selected_categories = st.multiselect(
            "按類別篩選",
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
                        "key": st.column_config.Column("支出編號", disabled=True, help=ccconfig.INFO_MSG_NOT_EDITABLE),
                        "category": st.column_config.TextColumn("類別"),
                        "item": st.column_config.TextColumn("項目"),
                        "amount": st.column_config.NumberColumn("金額", format="$%d"),
                     }
        )


    with col2:
        st.subheader("移除支出項目：")
        expense_id_list = df_expense["key"].tolist()
        chosen_expense_id = st.text_input("輸入支出編號移除：")
        with st.expander("確認移除支出項目", expanded=False):
            delete_button = st.button("確認", type="primary")

        if delete_button:
            if chosen_expense_id:
                if chosen_expense_id in expense_id_list:
                    remove_expense(chosen_expense_id)
                    st.success(f"已移除支出編號：{chosen_expense_id}，現在現在刷新頁面...")
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.warning("此支出編號不存在。")
            else:
                st.warning("請選擇支出編號。")


    # Show pie chart and table in 2 columns
    st.divider()
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("支出分佈")
        expense_by_category = filtered_df_expense.groupby("category")["amount"].sum()
        # Set Chinese font
        fontP = font_manager.FontProperties(fname="./fonts/SimHei.ttf")
        fontP.set_family('SimHei') 
        fontP.set_size(14)

        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            expense_by_category,
            labels=[f"{label} (${value:.2f})" for label, value in expense_by_category.items()],
            autopct="%1.1f%%",
        )
        ax.set_title(f"支出類別", fontproperties=fontP)
        for text in texts:
            text.set_fontproperties(fontP)
        plt.setp(autotexts, size=10, weight="bold")
        st.pyplot(fig)

    with col2:
        total_expense = expense_by_category.sum()
        selected_month_str = ", ".join(selected_month)
        st.subheader("總支出")
        st.write(f"時限：{selected_month_str}")

        expense_table = pd.DataFrame(expense_by_category)
        expense_table = expense_table.sort_values(by="amount", ascending=False)
        st.dataframe(
            expense_table, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "category": st.column_config.TextColumn("類別"),
                "amount": st.column_config.NumberColumn("金額", format="$%d")
                }
        )
        st.metric(label="HKD", value=f"${total_expense:.2f}")


if __name__ == "__main__":
    expense()