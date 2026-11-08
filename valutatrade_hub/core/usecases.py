"""Бизнес-логика ValutaTrade Hub.

Связывает модели, storage и реестр пользователей.
"""

from valutatrade_hub.core import storage
from valutatrade_hub.core.models import _USERS, User, register_user


def load_all_users() -> list[User]:
    """Загрузить всех пользователей из storage в память и реестр"""
    raw = storage.load_users_data()
    users = [User.from_dict(d) for d in raw]
    for user in users:
        register_user(user)
    return users


def get_user_by_username(username: str) -> User | None:
    """Найти пользователя по имени. None, если не найден"""
    for user in _USERS.values():
        if user.username == username:
            return user
    return None


def register(username: str, password: str) -> str:
    """Создать нового пользователя.
    Шаги по ТЗ:
    1. Проверить уникальность username в users.json.
    2. Сгенерировать user_id (автоинкремент).
    3. Захешировать пароль (sha256(password + salt), соль рядом).
    4. Сохранить пользователя в users.json.
    5. Создать пустой портфель (portfolios.json: user_id + пустой словарь).
    6. Вернуть сообщение об успехе.
    """

    load_all_users()

    existing = storage.load_users_data()
    if any(u["username"] == username for u in existing):
        raise ValueError(f"Имя пользователя '{username}' уже занято")

    new_id = max((u["user_id"] for u in existing), default=0) + 1

    user = User.create_user(new_id, username, password)

    existing.append(user.to_dict())
    storage.save_users_data(existing)

    portfolios = storage.load_portfolios_data()
    portfolios.append({"user_id": new_id, "wallets": {}})
    storage.save_portfolios_data(portfolios)

    register_user(user)

    return (
        f"Пользователь '{user.username}' зарегистрирован "
        f"(id={user.user_id}). "
        f"Войдите: login --username {user.username} --password ****"
    )
