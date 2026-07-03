"""
Sincroniza seguidores de GitHub:
- A quien te sigue y tú no sigues -> lo sigues.
- A quien sigues y no te sigue de vuelta -> lo dejas de seguir.
- Excepto los usuarios listados en KEEP_FOLLOWING (nunca se dejan de seguir).

Requiere un Personal Access Token (classic) con el scope "user:follow",
guardado como secreto GH_FOLLOW_TOKEN en el repo.
"""

import os
import time
import requests

TOKEN = os.environ["GH_FOLLOW_TOKEN"]
USERNAME = os.environ.get("GITHUB_USERNAME", "").strip()
KEEP = {
    u.strip().lower()
    for u in os.environ.get("KEEP_FOLLOWING", "").split(",")
    if u.strip()
}

API = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_username() -> str:
    global USERNAME
    if USERNAME:
        return USERNAME
    r = requests.get(f"{API}/user", headers=HEADERS)
    r.raise_for_status()
    USERNAME = r.json()["login"]
    return USERNAME


def paginate(url: str) -> set[str]:
    items = set()
    page = 1
    while True:
        r = requests.get(url, headers=HEADERS, params={"per_page": 100, "page": page})
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        items.update(u["login"].lower() for u in data)
        page += 1
        time.sleep(0.2)
    return items


def follow(user: str) -> None:
    r = requests.put(f"{API}/user/following/{user}", headers=HEADERS)
    if r.status_code == 204:
        print(f"Ahora sigues a {user}")
    else:
        print(f"No se pudo seguir a {user} (status {r.status_code})")


def unfollow(user: str) -> None:
    r = requests.delete(f"{API}/user/following/{user}", headers=HEADERS)
    if r.status_code == 204:
        print(f"Dejaste de seguir a {user}")
    else:
        print(f"No se pudo dejar de seguir a {user} (status {r.status_code})")


def main() -> None:
    me = get_username()
    print(f"Sincronizando seguidores de: {me}")
    print(f"Excepciones (nunca se dejan de seguir): {sorted(KEEP) or 'ninguna'}")

    followers = paginate(f"{API}/users/{me}/followers")
    following = paginate(f"{API}/users/{me}/following")

    to_follow = followers - following
    to_unfollow = (following - followers) - KEEP

    print(f"Seguidores: {len(followers)} | Siguiendo: {len(following)}")
    print(f"A seguir: {len(to_follow)} | A dejar de seguir: {len(to_unfollow)}")

    for user in sorted(to_follow):
        follow(user)
        time.sleep(0.5)

    for user in sorted(to_unfollow):
        unfollow(user)
        time.sleep(0.5)

    print("Sincronización terminada...")


if __name__ == "__main__":
    main()