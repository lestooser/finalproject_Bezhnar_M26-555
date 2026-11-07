import hashlib
import secrets
from datetime import UTC, datetime


class User:
    SALT_LENGTH = 16
    PASSWORD_MIN_LENGTH = 4

    def __init__(
        self,
        user_id: int,
        username: str,
        hashed_password: str,
        salt: str,
        registration_date: datetime,
    ) -> None:
        self._user_id = user_id
        self.username = username
        self.hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Имя пользователя не может быть пустым")
        self._username = value.strip()

    @property
    def hashed_password(self) -> str:
        return self._hashed_password

    @hashed_password.setter
    def hashed_password(self, value: str) -> None:
        if not value:
            raise ValueError("Хеш пароля не может быть пустым")
        self._hashed_password = value

    @property
    def salt(self) -> str:
        return self._salt

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

    @classmethod
    def create_user(cls, user_id: int, username: str, plain_password: str) -> "User":
        """
        Создание нового пользователя
        Соль генерируется заново, регистрационная дата - текущее UTC
        """
        cls._validate_password(plain_password)
        salt = secrets.token_hex(cls.SALT_LENGTH)
        hashed = hashlib.sha256((plain_password + salt).encode("utf-8")).hexdigest()
        return cls(user_id, username, hashed, salt, datetime.now(UTC))

    @classmethod
    def _validate_password(cls, password: str) -> None:
        """Проверить, что пароль не слишком короткий"""
        if len(password) < cls.PASSWORD_MIN_LENGTH:
            raise ValueError(
                f"Пароль должен быть не менее {cls.PASSWORD_MIN_LENGTH} символов"
            )

    def get_user_info(self) -> str:
        """Вернуть информацию о пользователе без секретов"""
        return (
            f"User ID: {self.user_id}\nUsername: {self.username}\n"
            f"Registration: {self.registration_date}"
        )

    def change_password(self, new_password: str) -> None:
        """Сменить пароль: проверить длину, сгенерировать новую соль, перехешировать"""
        self._validate_password(new_password)
        self._salt = secrets.token_hex(self.SALT_LENGTH)
        self._hashed_password = hashlib.sha256(
            (new_password + self._salt).encode("utf-8")
        ).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Проверить, совпадает ли переданный пароль с сохранённым хешем."""
        return (
            hashlib.sha256((password + self._salt).encode("utf-8")).hexdigest()
            == self._hashed_password
        )

    def __repr__(self) -> str:
        return f"User(user_id={self._user_id}, username={self._username!r})"
