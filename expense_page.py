import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import asyncio
from datetime import datetime
import utils
import time
import io
import base64

import database as db
import columns_categories_config as ccconfig

@st.cache_data
def fetch_all_expenses_cached():
    try:
        data = db.fetch_all_expenses()
        return data
    except Exception as e:
        st.error(f"讀取支出數據時發生錯誤：{e}")
        return []


def add_expense_item(expense_id, date, category, item, amount):
    parsed_date = datetime.strptime(str(date), "%Y-%m-%d")
    formatted_date = parsed_date.strftime("%d-%b-%y")

    async def add_expense_item_async(expense_id, formatted_date, category, item, amount):
        try:
            db.insert_expense(expense_id, formatted_date, category, item, amount)
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            st.cache_data.clear()

    coro = add_expense_item_async(expense_id, formatted_date, category, item, amount)

    with st.spinner("正在加入支出項目..."):
        asyncio.run(coro)

    st.success(ccconfig.SUCCESS_MSG)
    time.sleep(1)
    st.experimental_rerun()
    

def remove_expense(expense_id):
    async def remove_expense_async(expense_id):
        try:
            db.delete_expense(expense_id)
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            st.cache_data.clear()

    coro = remove_expense_async(expense_id)

    with st.spinner("正在移除支出項目..."):
        asyncio.run(coro)

    st.success(ccconfig.SUCCESS_MSG)
    time.sleep(1)
    st.experimental_rerun()


def expense():
    # Add expense form
    st.header("新增支出項目")
    CATEGORIES = ccconfig.EXPENSE_CATEGORIES # ["Rent", "Salaries", "Utilities", "Advertising", "Travel", "Others"]
    COLUMN_ORDER = ccconfig.EXPENSE_COLUMN_ORDER # ["key", "category", "item", "amount"] 
    expense_id = st.text_input("編號")
    date = st.date_input("日期")
    category = st.selectbox("會計項目", CATEGORIES)
    item = st.text_input("內容")
    amount = st.number_input("金額", step=1, min_value=0)
    if st.button("新增支出項目"):
        if any(field == "" for field in [date, category, item, amount]):
            st.warning(ccconfig.WARNING_MSG_FILL_ALL)
        else:
            add_expense_item(expense_id, date, category, item, amount)



    st.divider()
    expense_data = fetch_all_expenses_cached()
    df_expense = pd.DataFrame(expense_data, columns=COLUMN_ORDER) # initialize dataframe with the expected column order
    df_expense['month'] = df_expense['date'].apply(utils.format_month) # add a new column "month", by reading the "date" column
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
                        "date": st.column_config.TextColumn("日期"),
                        "category": st.column_config.TextColumn("會計項目"),
                        "item": st.column_config.TextColumn("內容"),
                        "amount": st.column_config.NumberColumn("金額", format="$%d"),
                     }
        )


    # Export excel file
    column_titles = {
        "key": "支出編號",
        "date": "日期",
        "category": "會計項目",
        "item": "內容",
        "amount": "金額"
    }
    excel_export_df = filtered_df_expense.rename(columns=column_titles)
    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        excel_export_df.to_excel(writer, sheet_name="支出報告", index=False)

    b64 = base64.b64encode(excel_buffer.getvalue()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="expense_data.xlsx" class="button">下載Excel支出報告</a>'
    st.markdown(href, unsafe_allow_html=True)


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

        # Display counts for certain categories





if __name__ == "__main__":
    expense()