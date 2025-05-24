import gspread
import os
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

load_dotenv()

def save_full_booking(user_id, username, order_type, cart_items, total_amount, booking_info=None):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    key_path = os.getenv("GOOGLE_KEY_PATH")
    creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
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
            "", "", "", "",  # пустые поля для бронирования
            order_type,
            "",  # адрес отсутствует
            order_details,
            total_amount,
            now
        ]

    sheet.append_row(row)