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
    st.header("Add New Herb")
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

        
    # ---- Display the current inventory table ----
    st.divider()
    st.header("Current Inventory")

    # All
    herb_id_list = df["key"].tolist()
    # print(df)
    # print(herb_id_list)

    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("All Herbs")
        st.dataframe(df, use_container_width=True)
    with col2:
        st.subheader("Update or delete")
        choose_herb_id = st.text_input("Input herb id to update or delete:")
        with st.expander("Update Inventory",expanded=False):
            new_unit_price = st.number_input("New unit price:", min_value=0, step=1)
            new_inventory = st.number_input("New inventory:", min_value=0, step=1)
            update_button = st.button("Update")
        with st.expander("Delete herb",expanded=False):
            delete_button = st.button("Delete")

        if update_button:
            if choose_herb_id:
                if choose_herb_id in herb_id_list:
                    db.update_herb(choose_herb_id, new_unit_price, new_inventory)
                    st.cache_data.clear()
                    st.success(f"Updated herb with id: {choose_herb_id}, please refresh the page.")
                else:
                    st.warning("Selected herb id does not exist.")
            else:
                st.warning("Please select a herb id to update.")
        if delete_button:
            if choose_herb_id:
                if choose_herb_id in herb_id_list:
                    db.delete_herb(choose_herb_id)
                    st.cache_data.clear()
                    st.success(f"Deleted herb with id: {choose_herb_id}, please refresh the page.")
                else:
                    st.warning("Selected herb id does not exist.")
            else:
                st.warning("Please select a herb id to delete.")
                

    st.divider()
    # Filter data for "Sam Gau" brand
    sam_gau_data = df[df["brand"] == "Sam Gau"]
    sam_gau_data = sam_gau_data[column_order]
    sam_gau_data = sam_gau_data.drop(columns=["brand"])
    st.subheader("Sam Gau")
    st.dataframe(sam_gau_data, hide_index = True)


    # Filter data for "Hoi Tin" brand
    hoi_tin_data = df[df["brand"] == "Hoi Tin"]
    hoi_tin_data = hoi_tin_data[column_order]
    hoi_tin_data = hoi_tin_data.drop(columns=["brand"])
    st.subheader("Hoi Tin")
    st.dataframe(hoi_tin_data, hide_index = True)

    # Filter data for other brands
    other_brands_data = df[(df["brand"] != "Sam Gau") & (df["brand"] != "Hoi Tin")]
    other_brands_data = other_brands_data[column_order]
    other_brands_data = other_brands_data.drop(columns=["brand"])

    st.subheader("Others")
    st.dataframe(other_brands_data, hide_index = True)


# Run the app
if __name__ == "__main__":
    inventory()
