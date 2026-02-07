# Ecolab Registration Bot

Telegram-бот для регистрации на два типа мероприятий Стартап-студии «ВоронаCreativeTech»: **Акселератор** и **Мероприятия**. Данные сохраняются в Google Sheets. Стек: aiogram 3, gspread.

## Возможности

- **Пользователи:** по команде `/start` выбор мероприятия → прохождение анкеты (инлайн-кнопки) → сохранение в таблицу. После регистрации можно снова нажать `/start` и зарегистрироваться на второе мероприятие или повторно.
- **Админы:** рассылка по выбранной аудитории (всем / только Акселератор / только Мероприятия), удаление сообщения рассылки у всех (`/delete` в ответ на него).

## Требования

- Python 3.10+
- Google-таблица с двумя листами: **«Мероприятия»** и **«Акселератор»** (заголовки создаёт бот при первой записи)
- Учётные данные: `.env` и `credentials.json` (сервисный аккаунт Google)

## Настройка

1. **Клонировать репозиторий и перейти в каталог.**

2. **Создать виртуальное окружение и установить зависимости:**

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

При ошибках SSL при установке:
`pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt`

3. **Переменные окружения:** скопировать `env.example` в `.env` и заполнить:

```bash
cp env.example .env
```

- `BOT_TOKEN` — токен от [@BotFather](https://t.me/BotFather)
- `SPREADSHEET_ID` — ID книги из URL таблицы (`.../d/SPREADSHEET_ID/...`)
- `ADMINS_IDS` — ID админов через запятую (необязательно; свой ID можно узнать у [@userinfobot](https://t.me/userinfobot))

4. **Google Sheets:** в корне проекта положить `credentials.json` (ключ сервисного аккаунта). Таблицу с указанным `SPREADSHEET_ID` нужно открыть для этого сервисного аккаунта (например, по email из ключа).

## Запуск

```bash
python bot.py
```

## Команды

| Команда   | Кто     | Описание |
|----------|--------|----------|
| `/start` | Все    | Выбор мероприятия и регистрация |
| `/send`  | Админы | Рассылка (сначала выбор аудитории, затем ввод текста) |
| `/delete` | Админы | Ответом на сообщение рассылки — удалить его у всех получателей |

## Структура проекта

```
├── bot.py              # Точка входа
├── config.py           # Конфиг из .env и константы
├── handlers/
│   ├── registration.py # Регистрация (оба мероприятия)
│   └── admin.py        # Рассылка и /delete
├── services/
│   ├── sheets.py       # Запись в Google Sheets, получение user_id по листам
│   └── broadcaster.py  # (не используется в текущей логике)
├── utils/
│   ├── states.py       # FSM-состояния
│   └── validators.py   # Валидация email, контакта, URL
├── env.example
├── requirements.txt
└── README.md
```

Файлы `.env` и `credentials.json` в репозиторий не попадают (см. `.gitignore`).
