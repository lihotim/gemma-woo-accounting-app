import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date

def generate_sample_income_data():
    categories = ["Consultation", "Herb sale", "Class", "Other"]
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 8, 31)

    data = []
    for _ in range(10):
        date = generate_random_date(start_date, end_date)
        item = f"Item{_ + 1}"
        category = random.choice(categories)
        amount = random.randint(50, 500)
        data.append({"Date": date, "Item": item, "Category": category, "Amount": amount})

    return data

def income():
    st.header("Income")

    # Display input fields for adding income entries
    date = st.date_input("Date")
    item = st.text_input("Item")
    category = st.selectbox("Category", ["Consultation", "Herb sale", "Class", "Other"])
    amount = st.number_input("Amount", step=1)
    
    if st.button("Add new Income item", disabled=True):
        print(f"Date: {date}, Item: {item}, Category: {category}, Amount: {amount}")

    st.subheader("Sample Data of Income")
    sample_income_data = generate_sample_income_data()
    df = pd.DataFrame(sample_income_data)
    st.dataframe(df)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Income by Category (Pie Chart)")
        # Create a pie chart to show incomes by category
        income_by_category = df.groupby("Category")["Amount"].sum()
        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            income_by_category,
            labels=[f"{label} (${value:.2f})" for label, value in income_by_category.items()],
            autopct="%1.1f%%",
        )
        ax.set_title("Income by Category")
        plt.setp(autotexts, size=10, weight="bold")
        st.pyplot(fig)


    with col2:
        st.subheader("Income by Category (Table)")
        # Display income by category in a table
        income_table = pd.DataFrame(income_by_category).reset_index()
        income_table.columns = ["Category", "Amount"]
        st.table(income_table)

    # Calculate and display total income
    total_income = income_by_category.sum()
    # st.subheader("Total Income")
    # st.write(f"${total_income:.2f}")
    st.metric(label = "Total Income", value = f"{total_income:.2f}")

if __name__ == "__main__":
    income()