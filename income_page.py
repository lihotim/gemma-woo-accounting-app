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
def fetch_all_incomes_cached():
    data = db.fetch_all_incomes()
    return data

def add_income_item(date, category, item, customer, amount):
    current_time = datetime.now().strftime("%H:%M:%S")
    full_datetime = f"{date.strftime('%Y-%m-%d')}-{current_time}"
    async def add_income_item_async(full_datetime, category, item, customer, amount):
        db.insert_income(full_datetime, category, item, customer, amount)
        st.cache_data.clear()
    coro = add_income_item_async(full_datetime, category, item, customer, amount)
    with st.spinner("正在加入收入數據..."):
        asyncio.run(coro)
    st.success(ccconfig.SUCCESS_MSG)
    time.sleep(1)
    st.experimental_rerun()

def remove_income(income_id):
    async def remove_income_async(income_id):
        db.delete_income(income_id)
        st.cache_data.clear()
    coro = remove_income_async(income_id)
    with st.spinner("正在移除收入數據..."):
        asyncio.run(coro)
    st.success(ccconfig.SUCCESS_MSG)
    time.sleep(1)
    st.experimental_rerun()


def income():
    # Add income form
    st.header("新增收入")
    CATEGORIES = ccconfig.INCOME_CATEGORIES # ["Consultation", "Herb Sale", "Class", "Others"]
    COLUMN_ORDER = ccconfig.INCOME_COLUMN_ORDER # ["key", "category", "item", "customer", "amount"]
    date = st.date_input("日期")
    category = st.selectbox("類別", CATEGORIES)
    item = st.text_input("項目")
    customer = st.text_input("客戶名稱")
    amount = st.number_input("金額", step=1, min_value=0)
    if st.button("新增收入項目"):
        if any(field == "" for field in [date, category, item, customer, amount]):
            st.warning(ccconfig.WARNING_MSG_FILL_ALL)
        else:
            add_income_item(date, category, item, customer, amount)


    st.divider()
    income_data = fetch_all_incomes_cached()
    df_income = pd.DataFrame(income_data, columns=COLUMN_ORDER) # initialize dataframe with the expected column order
    df_income['month'] = df_income['key'].apply(utils.format_month) # add a new column "month", by reading the date from "key"
    month_options = df_income['month'].unique() # list of months, e.g. ['2023 May' '2023 Jun' '2023 Jul' '2023 Aug']


    # Display all incomes and delete button in 2 columns (2:1)
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("收入項目：")

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
        filtered_df_income = df_income[
            (df_income['category'].isin(selected_categories)) &
            (df_income['month'].isin(selected_month))
        ]
        filtered_df_income = filtered_df_income.drop(columns=['month'])  # Drop the 'month' column
        st.dataframe(filtered_df_income, 
                     hide_index=True, 
                     use_container_width=True,
                     column_config={
                        "key": st.column_config.Column("收入編號", disabled=True, help=ccconfig.INFO_MSG_NOT_EDITABLE),
                        "category": st.column_config.TextColumn("類別"),
                        "item": st.column_config.TextColumn("項目"),
                        "customer": st.column_config.TextColumn("客戶名稱"),
                        "amount": st.column_config.NumberColumn("金額", format="$%d"),
                     }
        )

    with col2:
        st.subheader("移除收入項目：")
        income_id_list = df_income["key"].tolist()
        chosen_income_id = st.text_input("輸入收入編號移除：")
        with st.expander("確認移除收入項目", expanded=False):
            delete_button = st.button("確認", type="primary")

        if delete_button:
            if chosen_income_id:
                if chosen_income_id in income_id_list:
                    remove_income(chosen_income_id)
                    st.success(f"已移除收入編號： {chosen_income_id}，現在現在刷新頁面...")
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.warning("此收入編號不存在。")
            else:
                st.warning("請選擇收入編號。")


    # Show pie chart and table in 2 columns
    st.divider()
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("收入分佈")
        income_by_category = filtered_df_income.groupby("category")["amount"].sum()
        # Set Chinese font
        fontP = font_manager.FontProperties(fname="./fonts/SimHei.ttf")
        fontP.set_family('SimHei') 
        fontP.set_size(14)

        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            income_by_category,
            labels=[f"{label} (${value:.2f})" for label, value in income_by_category.items()],
            autopct="%1.1f%%",
        )    
        ax.set_title(f"收入類別", fontproperties=fontP)
        for text in texts:
            text.set_fontproperties(fontP)
        plt.setp(autotexts, size=10, weight="bold")
        st.pyplot(fig)

    with col2:
        total_income = income_by_category.sum()
        selected_month_str = ", ".join(selected_month)
        st.subheader("總收入")
        st.write(f"時限：{selected_month_str}")

        income_table = pd.DataFrame(income_by_category)
        income_table = income_table.sort_values(by="amount", ascending=False)
        st.dataframe(
            income_table, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "category": st.column_config.TextColumn("類別"),
                "amount": st.column_config.NumberColumn("金額", format="$%d")
                }
        )
        st.metric(label="HKD", value=f"${total_income:.2f}")

        # Display counts for certain categories
        for category in ccconfig.CATEGORIES_TO_COUNT: # ["Consultation", "Herb Sale"]
            category_count = filtered_df_income[filtered_df_income['category'] == category].shape[0]
            st.metric(label=f"{category}次數", value=category_count)


if __name__ == "__main__":
    income()