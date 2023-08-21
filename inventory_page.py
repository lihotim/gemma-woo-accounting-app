import streamlit as st
import pandas as pd
import asyncio
import time

import database as db
import columns_categories_config as ccconfig

@st.cache_data
def fetch_all_herbs_cache():
    data = db.fetch_all_herbs()
    return data


def add_new_herb(herb_id, brand, herb_name, unit_price, stock):
    async def add_new_herb_async(herb_id, brand, herb_name, unit_price, stock):
        db.insert_herb(herb_id, brand, herb_name, unit_price, stock)
        st.cache_data.clear()

    coro = add_new_herb_async(herb_id, brand, herb_name, unit_price, stock)
    with st.spinner("正在加入中藥數據..."):
        asyncio.run(coro)
    st.success(ccconfig.SUCCESS_MSG)
    time.sleep(1)
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
    with st.spinner("正在更新中藥數據..."):
        asyncio.run(coro)
    st.success(ccconfig.SUCCESS_MSG)
    time.sleep(1)
    st.experimental_rerun()


def remove_herb(herb_id):
    async def remove_herb_async(herb_id):
        db.delete_herb(herb_id)
        st.cache_data.clear()
    coro = remove_herb_async(herb_id)
    with st.spinner("正在移除中藥數據..."):
        asyncio.run(coro)
    st.success(ccconfig.SUCCESS_MSG)
    time.sleep(1)
    st.experimental_rerun()



def inventory():
    BRANDS = ccconfig.HERB_BRANDS # ["Sam Gau", "Hoi Tin", "Others"]
    COLUMN_ORDER = ccconfig.INVENTORY_COLUMN_ORDER # ["key", "brand", "herb_name", "unit_price", "inventory"]
    inventory_data = fetch_all_herbs_cache()
    df_inventory = pd.DataFrame(inventory_data, columns=COLUMN_ORDER) # initialize dataframe with the expected column order
    herb_id_list = df_inventory['key'].tolist() # list of all herb_id

    # Display input fields for adding new inventory entries
    st.header("新增中藥")
    herb_id = st.text_input("中藥編號")
    brand = st.selectbox("品牌", BRANDS)
    herb_name = st.text_input("中藥名稱")
    unit_price = st.number_input("來貨價", step=0.1)
    stock = st.number_input("數量", step=1)

    if st.button("新增中藥"):
        if any(field == "" for field in [herb_id, brand, herb_name, unit_price, stock]):
            st.warning(ccconfig.WARNING_MSG_FILL_ALL)
        elif herb_id in herb_id_list:
            st.warning("中藥編號已存在，請填寫另一個編號。")
        else:
            add_new_herb(herb_id, brand, herb_name, unit_price, stock)


        
    # Display the current inventory table (using st.data_editor)
    st.divider()
    st.header("現時存貨")

    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("編輯中藥數據：")
        selected_brand = st.multiselect(
        "按品牌篩選",
        options=BRANDS,
        default=BRANDS,
        )
        df_inventory = df_inventory[
            (df_inventory['brand'].isin(selected_brand))
        ]
        edited_df_inventory = st.data_editor(
            df_inventory, 
            use_container_width=True,
            num_rows="fixed",
            hide_index=True,
            column_config = {
                "key": st.column_config.Column("中藥編號", disabled=True, help=ccconfig.INFO_MSG_NOT_EDITABLE),
                "brand": st.column_config.TextColumn("品牌", disabled=True, help=ccconfig.INFO_MSG_NOT_EDITABLE),
                "herb_name": st.column_config.TextColumn("中藥名稱"),
                "unit_price": st.column_config.NumberColumn("來貨價", min_value=0, format="$%d"),
                "inventory": st.column_config.NumberColumn("數量", min_value=0, step=1),
            },
        )
        if edited_df_inventory is not None and not edited_df_inventory.equals(df_inventory):
            update_inventory(df_inventory, edited_df_inventory)
    
    with col2:
        st.subheader("移除中藥：")
        herb_id_list = df_inventory["key"].tolist()
        chosen_herb_id = st.text_input("輸入中藥編號移除：")
        with st.expander("確認移除中藥", expanded=False):
            delete_button = st.button("確認", type="primary")

        if delete_button:
            if chosen_herb_id:
                if chosen_herb_id in herb_id_list:
                    remove_herb(chosen_herb_id)
                    st.success(f"已移除中藥編號：{chosen_herb_id}，現在現在刷新頁面...")
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.warning("此中藥編號不存在。")
            else:
                st.warning("請選擇中藥編號。")
                

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
                "key": st.column_config.Column("中藥編號", disabled=True),
                "herb_name": st.column_config.TextColumn("中藥名稱"),
                "unit_price": st.column_config.NumberColumn("來貨價", format="$%d"),
                "inventory": st.column_config.NumberColumn("數量"),
            }
        )


if __name__ == "__main__":
    inventory()
