import streamlit as st
import pandas as pd
import utils
import matplotlib.pyplot as plt
import io
import base64
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

import database as db
import columns_categories_config as ccconfig

@st.cache_data
def fetch_all_incomes_cached():
    data = db.fetch_all_incomes()
    return data

@st.cache_data
def fetch_all_expenses_cached():
    data = db.fetch_all_expenses()
    return data

def convert_to_monthly_summary(df, month_options):
    if df.empty:
        return pd.DataFrame(columns=["month", "amount"])  # Return an empty DataFrame with the required columns
    summary_df = df.groupby('month', as_index=False)['amount'].sum()
    summary_df['month'] = pd.Categorical(summary_df['month'], categories=month_options, ordered=True)
    summary_df = summary_df.sort_values('month')
    return summary_df[['month', 'amount']] 


@st.cache_data
def get_income_expense_by_month(df_income_by_month, df_expense_by_month):
    df_income_expense_by_month = pd.merge(df_income_by_month, df_expense_by_month, on='month', how='outer')
    df_income_expense_by_month = df_income_expense_by_month.rename(columns={
        'amount_x': 'Income',
        'amount_y': 'Expense'
    })
    months_list = df_income_expense_by_month['month'].tolist()
    return df_income_expense_by_month, months_list


def create_word_report(dataframes):
    doc = Document()
    for title, df in dataframes.items():
        doc.add_heading(title, level=1)
        # Add table with gridlines
        table = doc.add_table(rows=df.shape[0] + 1, cols=df.shape[1])
        table.style = "Table Grid"
        # Set column headers
        for j, col_name in enumerate(df.columns):
            cell = table.cell(0, j)
            cell.text = col_name
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Fill data into the table
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                cell = table.cell(i + 1, j)
                cell.text = str(df.iat[i, j])
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    return doc
    

def statistics():
    st.header("Statistics")
    # st.write(f'(We want to look at the trend of income and expense from each category here)')
    
    income_data = fetch_all_incomes_cached()
    expense_data = fetch_all_expenses_cached()

    col1, col2 = st.columns(2)
    with col1:
        INCOME_CATEGORIES = ccconfig.INCOME_CATEGORIES # ["Consultation", "Herb Sale", "Class", "Others"]
        INCOME_COLUMN_ORDER = ccconfig.INCOME_COLUMN_ORDER # ["key", "category", "item", "customer", "amount"]
        df_income = pd.DataFrame(income_data, columns=INCOME_COLUMN_ORDER)
        df_income['month'] = df_income['key'].apply(utils.format_month) # add a new column "month", by reading the date from "key"
        month_options = df_income['month'].unique() # list of months, e.g. ['2023 May' '2023 Jun' '2023 Jul' '2023 Aug']
        # Display for checking only, will hide it
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
    if len(income_data) > 0:
        df_income_by_category = df_income.pivot_table(index='month', columns='category', values='amount', aggfunc='sum', fill_value=0)
        df_income_by_category.reset_index(inplace=True)
        df_income_by_category = df_income_by_category.set_index('month').reindex(month_options).reset_index()
        df_income_by_category = df_income_by_category[['month'] + INCOME_CATEGORIES]
    else:
        df_income_by_category = pd.DataFrame(columns=['month'] + INCOME_CATEGORIES)

    
    st.subheader("Income by category")
    st.dataframe(df_income_by_category, 
                    hide_index=True,
                    use_container_width=True,
                    column_config={"month": st.column_config.TextColumn("Month")}
                )


    with col2:
        EXPENSE_CATEGORIES = ccconfig.EXPENSE_CATEGORIES # ["Rent", "Salaries", "Utilities", "Advertising", "Travel", "Others"]
        EXPENSE_COLUMN_ORDER = ccconfig.EXPENSE_COLUMN_ORDER # ["key", "category", "item", "amount"]
        df_expense = pd.DataFrame(expense_data, columns=EXPENSE_COLUMN_ORDER)
        df_expense['month'] = df_expense['key'].apply(utils.format_month) # add a new column "month", by reading the date from "key"
        month_options = df_expense['month'].unique() # list of months, e.g. ['2023 May' '2023 Jun' '2023 Jul' '2023 Aug']
        # Display for checking only, will hide it
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
    if len(expense_data) > 0:
        df_expense_by_category = df_expense.pivot_table(index='month', columns='category', values='amount', aggfunc='sum', fill_value=0)
        df_expense_by_category.reset_index(inplace=True)
        df_expense_by_category = df_expense_by_category.set_index('month').reindex(month_options).reset_index()
        df_expense_by_category = df_expense_by_category[['month'] + EXPENSE_CATEGORIES]
    else:
        df_expense_by_category = pd.DataFrame(columns=['month'] + EXPENSE_CATEGORIES)


    st.subheader("Expense by category")
    st.dataframe(df_expense_by_category,
                    hide_index=True,
                    use_container_width=True,
                    column_config={"month": st.column_config.TextColumn("Month")},
                )


    if len(income_data) > 0 and len(expense_data) > 0:
        st.subheader("Total Income and Expense Summary")
        df_income_by_month = convert_to_monthly_summary(df_income, month_options)
        df_income_by_month = df_income_by_month.reset_index(drop=True)
        df_expense_by_month = convert_to_monthly_summary(df_expense, month_options)
        df_expense_by_month = df_expense_by_month.reset_index(drop=True)

        df_income_expense_by_month, months_list = get_income_expense_by_month(df_income_by_month, df_expense_by_month)
        df_income_expense_by_month["Net Income"] = df_income_expense_by_month["Income"] - df_income_expense_by_month["Expense"]
        st.dataframe(df_income_expense_by_month,
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                        "month": st.column_config.TextColumn("Month"),
                        "Income": st.column_config.NumberColumn("Total Income", format="$%d"),
                        "Expense": st.column_config.NumberColumn("Total Expense", format="$%d"),
                        "Net Income": st.column_config.NumberColumn("Net Income", format="$%d"),
                        }
                    )
        


        st.divider()
        st.subheader("Trend in Total Income and Expense")
        start_month, end_month = st.select_slider(
            'Select a time range:',
            options=months_list,
            value=(months_list[0], months_list[-1]) 
        )

        # Filter Line chart of "Income by category" by selected months
        df_income_by_category['month'] = pd.to_datetime(df_income_by_category['month'], format='%Y %b')
        df_income_by_category = df_income_by_category[
            (df_income_by_category['month'] >= pd.to_datetime(start_month, format='%Y %b')) & 
            (df_income_by_category['month'] <= pd.to_datetime(end_month, format='%Y %b'))
        ]
        df_income_by_category['month'] = df_income_by_category['month'].dt.strftime('%Y %b')

        # Filter # Line chart of "Expense by category" by selected months
        df_expense_by_category['month'] = pd.to_datetime(df_expense_by_category['month'], format='%Y %b')
        df_expense_by_category = df_expense_by_category[
            (df_expense_by_category['month'] >= pd.to_datetime(start_month, format='%Y %b')) & 
            (df_expense_by_category['month'] <= pd.to_datetime(end_month, format='%Y %b'))
        ]
        df_expense_by_category['month'] = df_expense_by_category['month'].dt.strftime('%Y %b')

        # Filter Line chart of "Total Income, Expense and Net Income" by selected months
        df_income_expense_by_month = df_income_expense_by_month[
            (df_income_expense_by_month['month'] >= start_month) & (df_income_expense_by_month['month'] <= end_month)
        ]


        # Display Line chart of "Income by category"
        plt.figure(figsize=(10, 4))
        plt.title('Income by category')
        for category in INCOME_CATEGORIES:
            plt.plot(df_income_by_category['month'], df_income_by_category[category], marker='^', label=category)
        plt.xlabel('Month')
        plt.ylabel('Amount')
        plt.legend()
        plt.grid(True)
        st.pyplot(plt)

        # Display Line chart of "Expense by category"
        plt.figure(figsize=(10, 4))
        plt.title('Expense by category')
        for category in EXPENSE_CATEGORIES:
            plt.plot(df_expense_by_category['month'], df_expense_by_category[category], marker='v', label=category)
        plt.xlabel('Month')
        plt.ylabel('Amount')
        plt.legend()
        plt.grid(True)
        st.pyplot(plt)

        # Display Line chart of "Total Income, Expense and Net Income"
        plt.figure(figsize=(10, 4))
        plt.title('Total Income, Expense and Net Income')
        plt.plot(df_income_expense_by_month['month'], df_income_expense_by_month['Income'], marker='^', label='Income')
        plt.plot(df_income_expense_by_month['month'], df_income_expense_by_month['Expense'], marker='v', label='Expense')
        plt.plot(df_income_expense_by_month['month'], df_income_expense_by_month['Net Income'], marker='o', label='Net Income')
        plt.xlabel('Month')
        plt.ylabel('Amount')
        plt.legend()
        plt.grid(True)
        st.pyplot(plt)


        # Export excel and word files
        st.divider()
        st.subheader("Download statistics files")
        # Export excel file
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            df_income_by_category.to_excel(writer, sheet_name="Income by Category", index=False)
            df_expense_by_category.to_excel(writer, sheet_name="Expense by Category", index=False)
            df_income_expense_by_month.to_excel(writer, sheet_name="Total Income & Expense Summary", index=False)

        b64 = base64.b64encode(excel_buffer.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="statistics.xlsx" class="button">Download Excel Report</a>'
        st.markdown(href, unsafe_allow_html=True)

        # Export word file
        dataframes = {
            "Income by Category": df_income_by_category,
            "Expense by Category": df_expense_by_category,
            "Total Income & Expense Summary": df_income_expense_by_month
        }
        doc = create_word_report(dataframes)
        doc_buffer = io.BytesIO()
        doc.save(doc_buffer)
        doc_buffer.seek(0)
        b64 = base64.b64encode(doc_buffer.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="statistics.docx" class="button">Download Word Report</a>'
        st.markdown(href, unsafe_allow_html=True)

    else:
        st.subheader("Total Income and Expense Summary")
        st.warning("Oops! It looks like either income or expense data is missing. To view the Total Income and Expense Summary and their trends, please make sure to import the necessary data.")


if __name__ == "__main__":
    statistics()