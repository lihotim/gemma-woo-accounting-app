from datetime import datetime

def format_month(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d-%H:%M:%S")
    return date_obj.strftime("%Y %b")