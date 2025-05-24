import gspread
import os
import json
from google.oauth2.service_account import Credentials
from datetime import datetime

def save_full_booking(user_id, username, order_type, cart_items, total_amount, booking_info=None):
    creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1ur9uxSVVt8b1ZaeBJ-Bkr1jQ2y_kYC6gtcaaMC13m8k/edit?usp=sharing"
    ).sheet1

    order_details = "\n".join([f"{item['name']} - {item.get('portion', 0)} шт." for item in cart_items])
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if booking_info:
        row = [
            username or "Неизвестно",
            str(user_id),
            booking_info.get("phone", ""),
            booking_info.get("date", ""),
            booking_info.get("time", ""),
            booking_info.get("count", ""),
            order_type,
            booking_info.get("address", ""),
            order_details,
            total_amount,
            now
        ]
    else:
        row = [
            username or "Неизвестно",
            str(user_id),
            "", "", "", "",  # пустые поля
            order_type,
            "",  # адрес
            order_details,
            total_amount,
            now
        ]

    sheet.append_row(row)