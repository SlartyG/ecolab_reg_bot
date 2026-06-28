"""
Динамический список админов.

Обновляется каждый час из Google Sheets (лист «Админы») в bot.py.
Хендлеры импортируют `get_admin_ids()` напрямую отсюда.
"""

# Глобальный список админов (обновляется из bot.py)
_admin_ids: list[int] = []


def get_admin_ids() -> list[int]:
    """Возвращает текущий список Telegram ID админов (копия)."""
    return list(_admin_ids)


def set_admin_ids(ids: list[int]) -> None:
    """Обновляет список админов (вызывается из bot.py)."""
    global _admin_ids
    _admin_ids = list(ids)
