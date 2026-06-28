from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Прокси для Telegram API (если api.telegram.org недоступен с сервера):
# http://user:pass@host:port или socks5://user:pass@host:port
TELEGRAM_PROXY = os.getenv("TELEGRAM_PROXY") or None
# Одна книга, листы: "Мероприятия", "Акселератор", "Админы"
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME_EVENTS = "Мероприятия"
SHEET_NAME_ACCELERATOR = "Акселератор"
SHEET_NAME_ADMINS = "Админы"
CREDENTIALS_FILE = "credentials.json"

# Выбор мероприятия при /start
EVENTS = {
    "accelerator": "Акселератор «ВоронаКреативТех»",
    "events": "Мероприятия Бизнес-студии «ВоронаКреативТех»",
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

# Ссылка на бота для прохождения теста (инлайн-кнопка «Пройти тест»)
TEST_BOT_LINK = os.getenv("TEST_BOT_LINK", "")

# Контакт поддержки (юзернейм с @ для приветственного сообщения)
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "VoronaHSE")
if not SUPPORT_USERNAME.startswith("@"):
    SUPPORT_USERNAME = "@" + SUPPORT_USERNAME
