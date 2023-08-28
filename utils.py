from datetime import datetime

def format_month(date_str):
    date_obj = datetime.strptime(date_str, "%d-%b-%y")
    return date_obj.strftime("%Y %b")