# Inventory page
HERB_BRANDS = ["三九", "海天", "其他"]
INVENTORY_COLUMN_ORDER = ["key", "brand", "herb_name", "unit_price", "inventory"] # same no. of columns as inventory_db, just in different order

# Income page
CATEGORIES_TO_COUNT = ["診症", "中藥零售"]
INCOME_CATEGORIES = ["診症", "中藥零售", "教學", "其他"]
INCOME_COLUMN_ORDER = ["key", "category", "item", "customer", "amount"] # same no. of columns as income_db, just in different order

# Expense page
EXPENSE_CATEGORIES = ["租金", "人工", "訂貨", "水電", "宣傳", "交通", "其他"]
EXPENSE_COLUMN_ORDER = ["key", "category", "item", "amount"] # same no. of columns as expense_db, just in different order

# messages
SUCCESS_MSG = "更新成功！現在刷新頁面..."
WARNING_MSG_FILL_ALL = "請填寫所有必填字段。"
INFO_MSG_NOT_EDITABLE = "提示：此欄不能編輯"