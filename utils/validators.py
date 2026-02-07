import re

def validate_email(email: str) -> bool:
    """
    Проверяет корректность email адреса
    
    Args:
        email: Строка с email адресом
        
    Returns:
        bool: True если email корректный, False если нет
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_telegram_contact(contact: str) -> bool:
    """
    Проверяет корректность telegram контакта (@username или телефон)
    
    Args:
        contact: Строка с контактом
        
    Returns:
        bool: True если контакт корректный, False если нет
    """
    # Проверка на @username
    if contact.startswith('@'):
        username_pattern = r'^@[a-zA-Z0-9_]{5,32}$'
        return bool(re.match(username_pattern, contact))
    
    # Проверка на телефонный номер (простая проверка)
    phone_pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(phone_pattern, contact))


def validate_url(url: str) -> bool:
    """
    Проверяет, что строка похожа на URL (http/https).
    """
    url = (url or "").strip()
    return url.startswith("http://") or url.startswith("https://")

