from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
# ID админов через запятую в .env (ADMINS_IDS=123,456) или значение по умолчанию
_admins_str = os.getenv("ADMINS_IDS")
ADMINS = [int(x.strip()) for x in _admins_str.split(",") if x.strip()]

# Одна книга, два листа: "Мероприятия" и "Акселератор"
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME_EVENTS = "Мероприятия"
SHEET_NAME_ACCELERATOR = "Акселератор"
CREDENTIALS_FILE = "credentials.json"

# Выбор мероприятия при /start
EVENTS = {
    "accelerator": "Акселератор «ВоронаCreativeTech»",
    "events": "Мероприятия Стартап-студии",
}

# Акселератор: направление (трек)
ACCELERATOR_TRACKS = {
    "urban": "Urban & TravelTech",
    "clean": "Clean & AgroTech",
    "good": "Tech for Good",
    "other": "Другое",
}

# Акселератор: этап реализации
ACCELERATOR_STAGES = {
    "idea": "Идея",
    "mvp": "MVP",
    "sales": "Продажи",
}

# Акселератор: выступление на PizzaPitch / Прожарке
PIZZAPITCH_CHOICES = {
    "yes": "Да",
    "no": "Нет",
    "maybe": "Возможно",
}

# Ссылка на положение о персональных данных
PERSONAL_DATA_POLICY_URL = "https://www.hse.ru/data_protection_regulation"

# Контакт поддержки (юзернейм с @ для приветственного сообщения)
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "VoronaHSE")
if not SUPPORT_USERNAME.startswith("@"):
    SUPPORT_USERNAME = "@" + SUPPORT_USERNAME
