import streamlit as st
import pandas as pd
import database as db
import asyncio

@st.cache_data
def fetch_all_herbs_cache():
    data = db.fetch_all_herbs()
    return data


def add_new_herb(herb_id, brand, herb_name, unit_price, stock):
    async def add_new_herb_async(herb_id, brand, herb_name, unit_price, stock):
        db.insert_herb(herb_id, brand, herb_name, unit_price, stock)
        st.cache_data.clear()

    coro = add_new_herb_async(herb_id, brand, herb_name, unit_price, stock)
    with st.spinner("Adding herb data..."):
        asyncio.run(coro)
    st.experimental_rerun()


def update_inventory(old_df, edited_df):
    different_rows = (old_df != edited_df).any(axis=1)
    herb_id = old_df[different_rows]['key'].values[0]
    for col in edited_df.columns:
        if edited_df[col][different_rows].values[0] != old_df[col][different_rows].values[0]:
            col_changed = col
            new_value = edited_df.loc[different_rows, col].values[0]
            if not isinstance(new_value, str):
                new_value = float(new_value)
            break

    async def update_herb_async(herb_id, col_changed, new_value):
        db.update_herb(herb_id, {f"{col_changed}": new_value})
        st.cache_data.clear()

    coro = update_herb_async(herb_id, col_changed, new_value)
    with st.spinner("Updating herb data..."):
        asyncio.run(coro)
    st.experimental_rerun()


def remove_herb(herb_id):
    async def remove_herb_async(herb_id):
        db.delete_herb(herb_id)
        st.cache_data.clear()
    coro = remove_herb_async(herb_id)
    with st.spinner("Removing herb data..."):
        asyncio.run(coro)
    st.experimental_rerun()



def inventory():
    COLUMN_ORDER = ["key", "brand", "herb_name", "unit_price", "inventory"]
    BRANDS = ["Sam Gau", "Hoi Tin", "Others"]
    data = fetch_all_herbs_cache()
    df_inventory = pd.DataFrame(data)
    df_inventory = df_inventory[COLUMN_ORDER]

    # Display input fields for adding new inventory entries
    st.header("Add New Herb")
    herb_id = st.text_input("Herb ID")
    brand = st.selectbox("Brand", BRANDS)
    herb_name = st.text_input("Herb Name")
    unit_price = st.number_input("Unit Price", step=0.1)
    stock = st.number_input("Stock", step=1)

    if st.button("Add New Herb"):
        add_new_herb(herb_id, brand, herb_name, unit_price, stock)

        
    # Display the current inventory table (using st.data_editor)
    st.divider()
    st.header("Current Inventory")

    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Edit Herbs:")
        edited_df_inventory = st.data_editor(
            df_inventory, 
            use_container_width=True,
            num_rows="fixed",
            hide_index=True,
            column_config = {
                "key": st.column_config.Column("Herb ID", disabled=True, help="Info: Not editable"),
                "brand": st.column_config.TextColumn("Brand"),
                "herb_name": st.column_config.TextColumn("Herb Name"),
                "unit_price": st.column_config.NumberColumn("Unit Price", min_value=0, format="$%d"),
                "inventory": st.column_config.NumberColumn("Inventory", min_value=0, step=1),
            },
        )
        if edited_df_inventory is not None and not edited_df_inventory.equals(df_inventory):
            update_inventory(df_inventory, edited_df_inventory)
    
    with col2:
        st.subheader("Remove a herb:")
        herb_id_list = df_inventory["key"].tolist()
        chosen_herb_id = st.text_input("Input Herb ID to remove it:")
        with st.expander("Confirm delete herb", expanded=False):
            delete_button = st.button("Confirm", type="primary")

        if delete_button:
            if chosen_herb_id:
                if chosen_herb_id in herb_id_list:
                    remove_herb(chosen_herb_id)
                    st.success(f"Deleted herb with id: {chosen_herb_id}, please refresh the page.")
                else:
                    st.warning("Selected herb id does not exist.")
            else:
                st.warning("Please select a herb id to delete.")
                

    st.divider()
    for brand in BRANDS:
        brand_data = df_inventory[df_inventory["brand"] == brand]
        brand_data = brand_data[COLUMN_ORDER]
        brand_data = brand_data.drop(columns=["brand"])
        st.subheader(brand)
        st.dataframe(
            brand_data, 
            hide_index=True,
            use_container_width=True,
            column_config={
                "key": st.column_config.Column("Herb ID", disabled=True, help="Info: Not editable"),
                "herb_name": st.column_config.TextColumn("Herb Name"),
                "unit_price": st.column_config.NumberColumn("Unit Price", format="$%d"),
                "inventory": st.column_config.NumberColumn("Inventory"),
            }
        )


if __name__ == "__main__":
    inventory()
