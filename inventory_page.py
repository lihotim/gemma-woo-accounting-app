import streamlit as st
import pandas as pd
import database as db


@st.cache_data
def fetch_all_herbs_cache():
    data = db.fetch_all_herbs()
    return data


def inventory():
    column_order = ["key", "brand", "herb_name", "unit_price", "inventory"]
    data = fetch_all_herbs_cache()
    df = pd.DataFrame(data)
    df = df[column_order]

    # Display input fields for adding new inventory entries
    st.header("Update Inventory")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Add New Herb")
        herb_id = st.text_input("Herb ID")
        brand = st.selectbox("Brand", ["Sam Gau", "Hoi Tin", "Others"])
        herb_name = st.text_input("Herb Name")
        unit_price = st.number_input("Unit Price", step=0.1)
        stock = st.number_input("Stock", step=1)

        if st.button("Add New Herb"):
            db.insert_herb(herb_id, brand, herb_name, unit_price, stock)
            st.cache_data.clear()
            data = fetch_all_herbs_cache()
            df = pd.DataFrame(data)
            df = df[column_order]
            st.success("Inventory entry added successfully!")

    with col2:
        st.subheader("Update Herb Info")
        # herb_id = st.text_input("Herb ID")
        # brand = st.selectbox("Brand", ["Sam Gau", "Hoi Tin", "Others"])
        # herb_name = st.text_input("Herb Name")
        # unit_price = st.number_input("Unit Price", step=0.1)
        # stock = st.number_input("Stock", step=1)

    # Display the current inventory table
    st.divider()
    st.header("Current Inventory")
    # st.dataframe(df)

    # col1, col2 = st.columns(2)
    sam_gau_data = df[df["brand"] == "Sam Gau"]
    sam_gau_data = sam_gau_data[column_order]
    st.subheader("Sam Gau")
    st.dataframe(sam_gau_data)

    # Filter data for "Hoi Tin" brand and display in col2
    hoi_tin_data = df[df["brand"] == "Hoi Tin"]
    hoi_tin_data = hoi_tin_data[column_order]
    st.subheader("Hoi Tin")
    st.dataframe(hoi_tin_data)

    # Filter data for other brands
    other_brands_data = df[(df["brand"] != "Sam Gau") & (df["brand"] != "Hoi Tin")]
    other_brands_data = other_brands_data[column_order]
    st.subheader("Others")
    st.dataframe(other_brands_data)


# Run the app
if __name__ == "__main__":
    inventory()
