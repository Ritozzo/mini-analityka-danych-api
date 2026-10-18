
import requests
import pandas as pd

BASE_URL = "https://jsonplaceholder.typicode.com"


"""Pobiera dane z wybranego endpointu API i zwraca je jako DataFrame."""
def fetch_data(endpoint):
    url = f"{BASE_URL}/{endpoint}"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    return response.json()


"""Pobiera użytkowników, posty i komentarze z API."""
def load_all_data():
    users = pd.DataFrame(fetch_data("users"))
    posts = pd.DataFrame(fetch_data("posts"))
    comments = pd.DataFrame(fetch_data("comments"))
    todos = pd.DataFrame(fetch_data("todos"))

    return users, posts, comments, todos
