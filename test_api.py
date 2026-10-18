import requests

url = "https://jsonplaceholder.typicode.com/users"

response = requests.get(url, timeout=15)
response.raise_for_status()

users = response.json()

print("Количество пользователей:", len(users))
print("Первый пользователь:")
print(users[0])