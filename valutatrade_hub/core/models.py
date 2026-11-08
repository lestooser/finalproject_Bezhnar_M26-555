import hashlib
import secrets
from datetime import UTC, datetime

EXCHANGE_RATES: dict[str, float] = {
    "USD": 1.0,
    "EUR": 1.0786,
    "GBP": 1.2386,
    "RUB": 0.01016,
    "BTC": 59337.21,
    "ETH": 3720.00,
    "SOL": 145.12,
}


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

    def to_dict(self) -> dict:
        """Сериализовать для JSON. Время - в ISO"""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Восстановить из JSON-словаря"""
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            hashed_password=data["hashed_password"],
            salt=data["salt"],
            registration_date=datetime.fromisoformat(data["registration_date"]),
        )


_USERS: dict[int, User] = {}


def register_user(user: User) -> None:
    _USERS[user.user_id] = user


def find_user_by_id(user_id: int) -> User:
    """Найти пользователя по id. ValueError, если не найден."""
    if user_id not in _USERS:
        raise ValueError(f"Пользователь с id={user_id} не найден")
    return _USERS[user_id]


class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0) -> None:
        self.currency_code = currency_code
        self.balance = balance

    @property
    def currency_code(self) -> str:
        return self._currency_code

    @currency_code.setter
    def currency_code(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Код валюты не может быть пустым")
        normalized_code = value.strip().upper()
        if not (2 <= len(normalized_code) <= 5):
            raise ValueError("Код валюты должен содержать от 2 до 5 символов")
        self._currency_code = normalized_code

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError("Баланс должен быть числом")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        self._balance = float(value)

    @staticmethod
    def _validate_amount(value: float) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError("Сумма должна быть числом")
        if value <= 0:
            raise ValueError("Сумма должна быть положительным числом")

    def deposit(self, amount: float) -> None:
        """Пополнить баланс на amount"""
        self._validate_amount(amount)
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        """Снять amount, если достаточно средств"""
        self._validate_amount(amount)
        if amount > self.balance:
            raise ValueError(
                f"Недостаточно средств: доступно {self._balance} "
                f"{self.currency_code}, требуется {amount} {self.currency_code}"
            )
        self.balance -= amount

    def get_balance_info(self) -> str:
        """Строка с текущим балансом для CLI."""
        return f"{self.currency_code}: {self.balance}"

    def __repr__(self) -> str:
        return f"Wallet({self.currency_code}, {self.balance})"

    def to_dict(self) -> dict:
        """Сериализация в JSON"""
        return {
            "currency_code": self.currency_code,
            "balance": self._balance,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Wallet":
        return cls(
            currency_code=data["currency_code"],
            balance=data["balance"],
        )


class Portfolio:
    def __init__(self, user_id: int, wallets: dict[str, Wallet] | None = None) -> None:
        self._user_id = user_id
        self._wallets: dict[str, Wallet] = wallets or {}

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def user(self) -> User:
        """Пользователь-владелец портфеля (lazy lookup по user_id)."""
        return find_user_by_id(self._user_id)

    @property
    def wallets(self) -> dict[str, Wallet]:
        """Копия словаря кошельков — защита от внешней мутации."""
        return dict(self._wallets)

    def add_currency(self, currency_code: str) -> Wallet:
        """Добавляет новый кошелёк в портфель (если его ещё нет)"""
        code = currency_code.strip().upper()
        if code in self._wallets:
            return self._wallets[code]
        wallet = Wallet(code)
        self._wallets[code] = wallet
        return wallet

    def get_total_value(self, base_currency: str = "USD") -> float:
        """Возвращает общую стоимость всех валют пользователя в указанной валюте"""
        base = base_currency.strip().upper()
        if base not in EXCHANGE_RATES:
            raise ValueError(f"Неизвестная базовая валюта '{base}'")
        base_rate = EXCHANGE_RATES[base]
        total_usd = 0.0

        for wallet in self._wallets.values():
            if wallet.currency_code not in EXCHANGE_RATES:
                continue
            total_usd += wallet.balance * EXCHANGE_RATES[wallet.currency_code]

        return total_usd / base_rate

    def get_wallet(self, currency_code: str) -> Wallet:
        """Возвращает кошелёк пользователя по его коду"""
        code = currency_code.strip().upper()
        if code not in self._wallets:
            raise ValueError(f"У вас нет кошелька '{code}'")
        return self._wallets[code]

    def __repr__(self) -> str:
        return f"Portfolio(user_id={self._user_id}, wallets={list(self._wallets)})"

    def to_dict(self) -> dict:
        """Сериализует объект в JSON"""
        return {
            "user_id": self._user_id,
            "wallets": {
                code: wallet.to_dict() for code, wallet in self._wallets.items()
            },
        }
