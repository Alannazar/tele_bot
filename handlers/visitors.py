from datetime import datetime

def save_visitor(user_id, username):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('visitors.txt', 'a', encoding='utf-8') as file:
        file.write(f"{now} | ID: {user_id} | Имя: {username}\n")