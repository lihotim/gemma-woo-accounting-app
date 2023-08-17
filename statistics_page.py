import streamlit as st
import pandas as pd
import database as db
import utils


# features we want:
# - Display bar charts to let use see the trend of each category (e.g. the income from "consultation" has increased, or the expense from "rent" has decreased)
# - change ALL fetch_all functions to async, for all pages (need?)
# - export graph as jpg, other data + graph as excel (or maybe word)
# - 

@st.cache_data
def fetch_all_incomes_cached():
    return db.fetch_all_incomes()
@st.cache_data
def fetch_all_expenses_cached():
    return db.fetch_all_expenses()


def convert_to_monthly_summary(df, month_options):
    summary_df = df.groupby('month', as_index=False)['amount'].sum()
    summary_df['month'] = pd.Categorical(summary_df['month'], categories=month_options, ordered=True)
    summary_df = summary_df.sort_values('month')
    return summary_df[['month', 'amount']] 


# @st.cache_data
# def get_income_by_month(income_data):
    #  # CATEGORIES = ["Consultation", "Herb sale", "Class", "Others"]
    # INCOME_COLUMN_ORDER = ["key", "category", "item", "customer", "amount"]
    # df_income = pd.DataFrame(income_data)
    # df_income = df_income[INCOME_COLUMN_ORDER] # rearrange column order
    # df_income['month'] = df_income['key'].apply(utils.format_month) # add a new column "month", by reading the date from "key"
    # month_options = df_income['month'].unique() # list of months, e.g. ['2023 May' '2023 Jun' '2023 Jul' '2023 Aug']
    # # Display for checking only, will hide it
    # st.dataframe(df_income,
    #                 hide_index=True, 
    #                 use_container_width=True,
    #                 column_config={
    #                 "key": st.column_config.Column("Income ID", disabled=True, help="Info: Not editable"),
    #                 "category": st.column_config.TextColumn("Category"),
    #                 "item": st.column_config.TextColumn("Item"),
    #                 "customer": st.column_config.TextColumn("Customer"),
    #                 "amount": st.column_config.NumberColumn("Amount", format="$%d"),
    #                 }
    #             )
    # df_income_by_month = convert_to_monthly_summary(df_income, month_options)
    # df_income_by_month = df_income_by_month.reset_index(drop=True)
    # return df_income_by_month

# @st.cache_data
# def get_expense_by_month(expense_data):
    # # CATEGORIES = ["Rent", "Salaries", "Supplies", "Utilities", "Advertising", "Travel", "Others"]
    # EXPENSE_COLUMN_ORDER = ["key", "category", "item", "amount"]
    # df_expense = pd.DataFrame(expense_data)
    # df_expense = df_expense[EXPENSE_COLUMN_ORDER] # rearrange column order
    # df_expense['month'] = df_expense['key'].apply(utils.format_month) # add a new column "month", by reading the date from "key"
    # month_options = df_expense['month'].unique() # list of months, e.g. ['2023 May' '2023 Jun' '2023 Jul' '2023 Aug']
    # # Display for checking only, will hide it
    # st.dataframe(df_expense,
    #                 hide_index=True, 
    #                 use_container_width=True,
    #                 column_config={
    #                 "key": st.column_config.Column("Expense ID", disabled=True, help="Info: Not editable"),
    #                 "category": st.column_config.TextColumn("Category"),
    #                 "item": st.column_config.TextColumn("Item"),
    #                 "amount": st.column_config.NumberColumn("Amount", format="$%d"),
    #                 }
    #             )
    # df_expense_by_month = convert_to_monthly_summary(df_expense, month_options)
    # df_expense_by_month = df_expense_by_month.reset_index(drop=True)
    # return df_expense_by_month


@st.cache_data
def get_income_expense_by_month(df_income_by_month, df_expense_by_month):
    df_income_expense_by_month = pd.merge(df_income_by_month, df_expense_by_month, on='month', how='outer')
    df_income_expense_by_month = df_income_expense_by_month.rename(columns={
        'amount_x': 'Income',
        'amount_y': 'Expense'
    })
    months_list = df_income_expense_by_month['month'].tolist()
    return df_income_expense_by_month, months_list



def statistics():
    st.header("Statistics")
    st.write(f'(We want to look at the trend of income and expense from each category here)')
    
    income_data = fetch_all_incomes_cached()
    expense_data = fetch_all_expenses_cached()

    col1, col2 = st.columns(2)
    with col1:
        # df_income_by_month = get_income_by_month(income_data)
        INCOME_CATEGORIES = ["Consultation", "Herb sale", "Class", "Others"]
        INCOME_COLUMN_ORDER = ["key", "category", "item", "customer", "amount"]
        df_income = pd.DataFrame(income_data)
        df_income = df_income[INCOME_COLUMN_ORDER] # rearrange column order
        df_income['month'] = df_income['key'].apply(utils.format_month) # add a new column "month", by reading the date from "key"
        month_options = df_income['month'].unique() # list of months, e.g. ['2023 May' '2023 Jun' '2023 Jul' '2023 Aug']
        # print(month_options)
        # Display for checking only, will hide it
        st.dataframe(df_income,
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
        # print(df_income)

    df_income_by_category = df_income.pivot_table(index='month', columns='category', values='amount', aggfunc='sum', fill_value=0)
    df_income_by_category.reset_index(inplace=True)
    df_income_by_category = df_income_by_category.set_index('month').reindex(month_options).reset_index()
    df_income_by_category = df_income_by_category[['month'] + INCOME_CATEGORIES]
    st.subheader("Income by category")
    st.dataframe(df_income_by_category, 
                    hide_index=True,
                    column_config={"month": st.column_config.TextColumn("Month")}
                )
        # print(df_income_by_category)


    with col2:
        # df_expense_by_month = get_expense_by_month(expense_data)
        EXPENSE_CATEGORIES = ["Rent", "Salaries", "Supplies", "Utilities", "Advertising", "Travel", "Others"]
        EXPENSE_COLUMN_ORDER = ["key", "category", "item", "amount"]
        df_expense = pd.DataFrame(expense_data)
        df_expense = df_expense[EXPENSE_COLUMN_ORDER] # rearrange column order
        df_expense['month'] = df_expense['key'].apply(utils.format_month) # add a new column "month", by reading the date from "key"
        month_options = df_expense['month'].unique() # list of months, e.g. ['2023 May' '2023 Jun' '2023 Jul' '2023 Aug']
        # Display for checking only, will hide it
        st.dataframe(df_expense,
                        hide_index=True, 
                        use_container_width=True,
                        column_config={
                        "key": st.column_config.Column("Expense ID", disabled=True, help="Info: Not editable"),
                        "category": st.column_config.TextColumn("Category"),
                        "item": st.column_config.TextColumn("Item"),
                        "amount": st.column_config.NumberColumn("Amount", format="$%d"),
                        }
                    )
        # print(df_expense)
    df_expense_by_category = df_expense.pivot_table(index='month', columns='category', values='amount', aggfunc='sum', fill_value=0)
    df_expense_by_category.reset_index(inplace=True)
    df_expense_by_category = df_expense_by_category.set_index('month').reindex(month_options).reset_index()
    df_expense_by_category = df_expense_by_category[['month'] + EXPENSE_CATEGORIES]
    st.subheader("Expense by category")
    st.dataframe(df_expense_by_category,
                    hide_index=True,
                    column_config={"month": st.column_config.TextColumn("Month")},
                )



    st.subheader("Total Income and Expense Summary")
    df_income_by_month = convert_to_monthly_summary(df_income, month_options)
    df_income_by_month = df_income_by_month.reset_index(drop=True)
    df_expense_by_month = convert_to_monthly_summary(df_expense, month_options)
    df_expense_by_month = df_expense_by_month.reset_index(drop=True)
    df_income_expense_by_month, months_list = get_income_expense_by_month(df_income_by_month, df_expense_by_month)
    st.dataframe(df_income_expense_by_month,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                    "month": st.column_config.TextColumn("Month"),
                    "Income": st.column_config.NumberColumn("Total Income", format="$%d"),
                    "Expense": st.column_config.NumberColumn("Total Expense", format="$%d"),
                    }
                )
    start_month, end_month = st.select_slider(
        'Select a time range:',
        options=months_list,
        value=(months_list[0], months_list[-1]) 
    )

    df_income_expense_by_month = df_income_expense_by_month[
        (df_income_expense_by_month['month'] >= start_month) &
        (df_income_expense_by_month['month'] <= end_month)
    ]
    st.line_chart(df_income_expense_by_month, x="month", use_container_width=True)



if __name__ == "__main__":
    statistics()