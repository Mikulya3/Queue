from django.test import TestCase



import requests

def get_operators():
    response = requests.get('http://localhost:8000/operators/')
    if response.status_code == 200:
        operators = response.json()
        for operator in operators:
            print(f"Имя пользователя: {operator['name']}")
            print(f"Номер окна: {operator['window_number']}")
            print("--------------------")
    else:
        print("Ошибка при получении данных.")

get_operators()


