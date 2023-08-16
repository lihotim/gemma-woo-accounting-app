import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import database as db


@st.cache_data
def fetch_all_incomes_cached():
    return db.fetch_all_incomes()
@st.cache_data
def fetch_all_expenses_cached():
    return db.fetch_all_expenses()


def statistics():
    st.header("Statistics")
    
    # dummy_df = pd.DataFrame(
    #     {
    #         "key": ["a1", "b1", "c1", "d1", "e1"],
    #         "unit_price": [100, 200, 300, 400, 500],
    #         "amount": [10, 20, 30, 40, 50],
    #     }
    # )
    # if "df_value" not in st.session_state:
    #     st.session_state.df_value = dummy_df

    # def update_st_editor(old_df, edited_df):
    #     print(old_df)
    #     print(edited_df)
    #     different_rows = (old_df != edited_df).any(axis=1)
    #     key_different = old_df[different_rows]['key'].values[0]
    #     for col in edited_df.columns:
    #         if edited_df[col][different_rows].values[0] != old_df[col][different_rows].values[0]:
    #             col_different = col
    #             new_value = edited_df[col][different_rows].values[0]
    #             break
    #     print(f"key: {key_different}")
    #     print(f"{col_different}: {new_value}")

    # edited_df = st.data_editor(
    #     dummy_df,
    #     key="editor",
    #     num_rows="dynamic",
    # )

    # if edited_df is not None and not edited_df.equals(st.session_state["df_value"]):
    #     update_st_editor(st.session_state["df_value"], edited_df)
    #     st.session_state["df_value"] = edited_df

    # st.divider()
    # st.divider()



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