import pandas as pd


"""Oblicza podstawowe wskaźniki dotyczące aktywności użytkowników."""
def calculate_metrics(users, posts, comments, todos):

    # Oblicza liczbę wszystkich użytkowników, postów i komentarzy.
    total_users = len(users)
    total_posts = len(posts)
    total_comments = len(comments)
    total_todos = len(todos)

    # Zlicza zadania oznaczone jako wykonane.
    completed_todos = int(todos["completed"].sum())

    # Oblicza średnią liczbę postów przypadających na jednego użytkownika.
    # Jeśli nie ma użytkowników, zwraca 0, aby uniknąć dzielenia przez zero.
    posts_per_user = (
        total_posts / total_users if total_users else 0
    )

    # Oblicza średnią liczbę komentarzy przypadających na jeden post.
    # Jeśli nie ma postów, wynikiem jest 0.
    comments_per_post = (
        total_comments / total_posts if total_posts else 0
    )

    # Oblicza procent wykonanych zadań w stosunku do wszystkich zadań.
    completed_percentage = (
        completed_todos / total_todos * 100
        if total_todos else 0
    )

    # Zwraca wszystkie wskaźniki w jednym słowniku.
    return {
        "total_users": total_users,
        "total_posts": total_posts,
        "total_comments": total_comments,
        "total_todos": total_todos,
        "completed_todos": completed_todos,
        "posts_per_user": posts_per_user,
        "comments_per_post": comments_per_post,
        "completed_percentage": completed_percentage,
    }

"""Przygotowuje zestawienie aktywności każdego użytkownika."""
def get_user_activity(users, posts, todos):

    # Grupuje posty według identyfikatora użytkownika.
    # Następnie zlicza, ile postów opublikował każdy użytkownik.
    post_counts = (
        posts.groupby("userId")
        .size()
        .rename("post_count")
    )

    # Grupuje zadania według identyfikatora użytkownika.
    # Funkcja sum() zlicza wykonane zadania, a count() wszystkie zadania.
    todo_stats = (
        todos.groupby("userId")["completed"]
        .agg(["sum", "count"])
        .rename(columns={
            "sum": "completed_todos",
            "count": "total_todos",
        })
    )

    # Tworzy tabelę zawierającą identyfikatory i nazwy użytkowników.
    activity = users[["id", "name"]].copy()

    # Łączy dane użytkowników z liczbą opublikowanych przez nich postów.
    activity = activity.merge(
        post_counts,
        left_on="id",
        right_index=True,
        how="left",
    )

    # Dodaje liczbę wszystkich i wykonanych zadań każdego użytkownika.
    activity = activity.merge(
        todo_stats,
        left_on="id",
        right_index=True,
        how="left",
    )

    # Wskazuje kolumny zawierające liczby.
    count_columns = [
        "post_count",
        "completed_todos",
        "total_todos",
    ]

    # Zamienia brakujące wartości na 0 i konwertujemy je na liczby całkowite.
    activity[count_columns] = (
        activity[count_columns].fillna(0).astype(int)
    )

    # Oblicza procent wykonanych zadań w stosunku do wszystkich zadań.
    activity["todo_completion_pct"] = (
        activity["completed_todos"]
        / activity["total_todos"].replace(0, float("nan"))
        * 100
    ).fillna(0)

    return activity

"""Przygotowuje zestawienie postów według liczby komentarzy."""
def get_post_comment_counts(posts, comments):
    
    # Grupuje komentarze według identyfikatora posta.
    comment_counts = (
        comments.groupby("postId")
        .size()
        .rename("comment_count")
    )

    # Tworzy nową tabelę, łącząc dane o postach z liczbą komentarzy.
    result = posts[["id", "userId", "title"]].merge(
        comment_counts,
        left_on="id",
        right_index=True,
        how="left",
    )

    # Zamienia brakujące wartości w kolumnie "comment_count" na 0 i konwertuje je na liczby całkowite.
    result["comment_count"] = (
        result["comment_count"].fillna(0).astype(int)
    )

    # Sortuje wyniki według liczby komentarzy w kolejności malejącej i resetuje indeksy.
    return result.sort_values(
        "comment_count",
        ascending=False,
    ).reset_index(drop=True)
