import streamlit as st
import plotly.express as px

from data import load_all_data
from analysis import calculate_metrics, get_user_activity, get_post_comment_counts


# Konfiguracja strony aplikacji: tytuł karty przeglądarki i szeroki układ strony.
st.set_page_config(
    page_title="Mini-analityka danych z API",
    layout="wide",
)

# Wyświetlenie głównego tytułu i opisu aplikacji.
st.title("📊 Mini-analityka danych z API")
st.write(
    "Interaktywny dashboard analityczny korzystający "
    "z publicznego API JSONPlaceholder."
)

# Wyświetlenie ustawień i informacji o źródle danych w panelu bocznym.
st.sidebar.header("Ustawienia dashboardu")
st.sidebar.write(
    "Źródło danych: JSONPlaceholder"
)

# Przycisk usuwa dane z pamięci podręcznej, umożliwiając ich ponowne pobranie.
if st.sidebar.button("Odśwież dane"):
    st.cache_data.clear()

try:
    # Wyświetlenie komunikatu podczas pobierania danych z API.
    with st.spinner("Pobieranie danych z API..."):
        # Pobranie danych o użytkownikach, postach, komentarzach i zadaniach.
        users, posts, comments, todos = load_all_data()

    # Obliczenie podstawowych wskaźników na podstawie pobranych danych.
    metrics = calculate_metrics(users, posts, comments, todos)

    # Przygotowanie zestawienia aktywności poszczególnych użytkowników.
    activity = get_user_activity(users, posts, todos)

    # Przygotowanie zestawienia postów wraz z liczbą komentarzy.
    post_stats = get_post_comment_counts(posts, comments)

except Exception as error:
    # Wyświetlenie komunikatu o błędzie, jeśli pobieranie lub przetwarzanie
    # danych zakończy się niepowodzeniem.
    st.error(f"Nie udało się pobrać danych: {error}")

    # Zatrzymanie wykonywania aplikacji w przypadku wystąpienia błędu.
    st.stop()


# Sekcja prezentująca najważniejsze wskaźniki analityczne.
st.header("Najważniejsze wskaźniki")

# Podział sekcji na cztery kolumny.
col1, col2, col3, col4 = st.columns(4)

# Wyświetlenie całkowitej liczby użytkowników.
col1.metric(
    "Liczba użytkowników",
    metrics["total_users"],
)

# Wyświetlenie całkowitej liczby postów.
col2.metric(
    "Liczba postów",
    metrics["total_posts"],
)

# Wyświetlenie średniej liczby komentarzy przypadających na jeden post.
col3.metric(
    "Komentarze na post",
    f'{metrics["comments_per_post"]:.2f}',
)

# Wyświetlenie procentowego udziału wykonanych zadań.
col4.metric(
    "Wykonane zadania (%)",
    f'{metrics["completed_percentage"]:.1f}%',
)


# Sekcja prezentująca dodatkowe statystyki dotyczące danych.
st.subheader("Podsumowanie")

# Podział sekcji na trzy kolumny.
col5, col6, col7 = st.columns(3)

# Wyświetlenie całkowitej liczby komentarzy.
col5.metric(
    "Liczba komentarzy",
    metrics["total_comments"],
)

# Wyświetlenie średniej liczby postów przypadających na jednego użytkownika.
col6.metric(
    "Średnia liczba postów na użytkownika",
    f'{metrics["posts_per_user"]:.1f}',
)

# Wyświetlenie liczby wykonanych zadań w stosunku do wszystkich zadań.
col7.metric(
    "Wykonane zadania",
    f'{metrics["completed_todos"]} / {metrics["total_todos"]}',
)


# Wykres 1: liczba postów opublikowanych przez poszczególnych użytkowników.
st.header("Aktywność użytkowników")

# Utworzenie wykresu słupkowego uporządkowanego według liczby postów malejąco.
activity_chart = px.bar(
    activity.sort_values("post_count", ascending=False),
    x="name",
    y="post_count",
    title="Liczba postów według użytkowników",
    labels={
        "name": "Użytkownik",
        "post_count": "Liczba postów",
    },
)

# Obrócenie etykiet osi poziomej w celu poprawienia czytelności wykresu.
activity_chart.update_layout(
    xaxis_tickangle=-45,
)

# Wyświetlenie wykresu w szerokości dostępnej w aplikacji.
st.plotly_chart(activity_chart, use_container_width=True)


# Wykres 2: porównanie liczby wykonanych i niewykonanych zadań.
st.header("Realizacja zadań")

# Obliczenie liczby zadań wykonanych i pozostałych do wykonania.
completed_count = metrics["completed_todos"]
pending_count = metrics["total_todos"] - completed_count

# Utworzenie wykresu kołowego z pustym środkiem, przedstawiającego status zadań.
todo_chart = px.pie(
    names=["Wykonane", "Niewykonane"],
    values=[completed_count, pending_count],
    title="Porównanie wykonanych i niewykonanych zadań",
    hole=0.4,
)

# Wyświetlenie wykresu kołowego.
st.plotly_chart(todo_chart, use_container_width=True)


# Wykres 3: pięć postów z największą liczbą komentarzy.
st.header("5 najczęściej komentowanych postów")

# Wybranie pięciu pierwszych postów z zestawienia posortowanego według liczby komentarzy.
top_posts = post_stats.head(5).copy()

# Skrócenie tytułów postów do 35 znaków, aby poprawić czytelność etykiet.
top_posts["short_title"] = top_posts["title"].str.slice(0, 35)

# Utworzenie poziomego wykresu słupkowego prezentującego liczbę komentarzy.
top_chart = px.bar(
    top_posts.sort_values("comment_count"),
    x="comment_count",
    y="short_title",
    orientation="h",
    title="5 postów z największą liczbą komentarzy",
    labels={
        "comment_count": "Liczba komentarzy",
        "short_title": "Tytuł posta",
    },
)

# Wyświetlenie wykresu w aplikacji.
st.plotly_chart(top_chart, use_container_width=True)


# Sekcja zawierająca szczegółowe tabele z danymi.
# Każdy panel można rozwinąć, aby wyświetlić dodatkowe informacje.
with st.expander("Wyświetl dane o aktywności użytkowników"):
    # Wyświetlenie tabeli z liczbą postów i statystykami zadań każdego użytkownika.
    st.dataframe(
        activity[
            [
                "name",
                "post_count",
                "completed_todos",
                "total_todos",
                "todo_completion_pct",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

# Panel zawierający wszystkie posty i przypisaną do nich liczbę komentarzy.
with st.expander("Wyświetl wszystkie posty i liczbę komentarzy"):
    st.dataframe(
        post_stats,
        use_container_width=True,
        hide_index=True,
    )

# Panel zawierający surowe dane pobrane bezpośrednio z API.
with st.expander("Wyświetl surowe dane z API"):

    # Wyświetlenie tabeli użytkowników.
    st.subheader("Użytkownicy")
    st.dataframe(users, use_container_width=True)

    # Wyświetlenie tabeli postów.
    st.subheader("Posty")
    st.dataframe(posts, use_container_width=True)

    # Wyświetlenie tabeli komentarzy.
    st.subheader("Komentarze")
    st.dataframe(comments, use_container_width=True)

    # Wyświetlenie tabeli zadań.
    st.subheader("Zadania")
    st.dataframe(todos, use_container_width=True)

# Wyświetlenie informacji o źródle danych i edukacyjnym charakterze aplikacji.
st.caption(
    "Źródło danych: JSONPlaceholder. "
    "Zbiór danych ma charakter demonstracyjny i służy celom edukacyjnym."
)