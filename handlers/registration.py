from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from datetime import datetime

from utils.states import ChoosingEvent, AcceleratorStates, EventStates
from utils.validators import validate_email, validate_telegram_contact, validate_url
from services.sheets import GoogleSheetsService
from config import (
    EVENTS,
    ACCELERATOR_TRACKS,
    ACCELERATOR_STAGES,
    PIZZAPITCH_CHOICES,
    PERSONAL_DATA_POLICY_URL,
    SUPPORT_USERNAME,
    ADMINS,
)

router = Router()
sheets_service = GoogleSheetsService()

BACK_BTN = InlineKeyboardButton(text="◀️ Назад", callback_data="nav:back")

# --- Инлайн-клавиатуры ---
def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[BACK_BTN]])


def with_back(kb: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    rows = [list(row) for row in kb.inline_keyboard]
    rows.append([BACK_BTN])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def event_choice_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=EVENTS["events"], callback_data="ev:evs")],
        [InlineKeyboardButton(text=EVENTS["accelerator"], callback_data="ev:acc")],
    ])

def yes_no_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="yn:y"),
            InlineKeyboardButton(text="Нет", callback_data="yn:n"),
        ],
    ])

def consent_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, я ознакомился", callback_data="consent")],
    ])

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data="conf:y"),
            InlineKeyboardButton(text="✏️ Изменить", callback_data="conf:e"),
        ],
    ])

def track_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=v, callback_data=f"tr:{k}")] for k, v in ACCELERATOR_TRACKS.items()
    ])

def stage_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=v, callback_data=f"st:{k}")] for k, v in ACCELERATOR_STAGES.items()
    ])

def pizzapitch_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=v, callback_data=f"pz:{k}")] for k, v in PIZZAPITCH_CHOICES.items()
    ])


# --- Тексты и клавиатуры шагов (для перехода вперёд и «Назад») ---
ACC_INTRO = "Регистрация в Акселератор «ВоронаCreativeTech».\nВведите ваши ФИО:"
EV_INTRO = "Регистрация на мероприятия Бизнес-студии.\nВведите ваши ФИО:"
CONSENT_TEXT = (
    "Я подтверждаю, что лично ознакомился с Положением об обработке "
    "персональных данных НИУ ВШЭ, вправе предоставлять свои персональные "
    "данные и давать согласие на их обработку.\n\n"
    f"Ссылка на положение: {PERSONAL_DATA_POLICY_URL}"
)


def acc_step_prompt(state: AcceleratorStates):
    prompts = {
        AcceleratorStates.waiting_for_name: (ACC_INTRO, back_kb()),
        AcceleratorStates.waiting_for_project_name: ("Название проекта:", back_kb()),
        AcceleratorStates.waiting_for_email: ("Электронная почта:", back_kb()),
        AcceleratorStates.waiting_for_tg: (
            "Ваш Telegram-аккаунт (@username или номер телефона):",
            back_kb(),
        ),
        AcceleratorStates.waiting_for_track: ("Направление (трек):", with_back(track_kb())),
        AcceleratorStates.waiting_for_stage: (
            "Этап реализации проекта:",
            with_back(stage_kb()),
        ),
        AcceleratorStates.waiting_for_description: ("Краткое описание проекта:", back_kb()),
        AcceleratorStates.waiting_for_pizzapitch: (
            "Хотите выступить на PizzaPitch или Прожарке стартапов?",
            with_back(pizzapitch_kb()),
        ),
        AcceleratorStates.waiting_for_presentation_url: (
            "Пришлите ссылку на презентацию вашего продукта/проекта (URL):",
            back_kb(),
        ),
        AcceleratorStates.waiting_for_team: ("ФИО и роль членов команды:", back_kb()),
        AcceleratorStates.waiting_for_hse: ("Вы из НИУ ВШЭ?", with_back(yes_no_kb())),
        AcceleratorStates.waiting_for_consent: (CONSENT_TEXT, with_back(consent_kb())),
    }
    return prompts[state]


def ev_step_prompt(state: EventStates):
    prompts = {
        EventStates.waiting_for_name: (EV_INTRO, back_kb()),
        EventStates.waiting_for_hse: (
            "Вы из ВШЭ? (важно для заказа пропуска для гостей не из ВШЭ)",
            with_back(yes_no_kb()),
        ),
        EventStates.waiting_for_edu_program: (
            "Ваша образовательная программа (для выпускников — программа по диплому):",
            back_kb(),
        ),
        EventStates.waiting_for_tg: (
            "Ваш Telegram-аккаунт (@username или номер телефона):",
            back_kb(),
        ),
        EventStates.waiting_for_question: (
            "Ваш вопрос спикерам или организаторам (можно пропустить — отправьте «-»):",
            back_kb(),
        ),
        EventStates.waiting_for_consent: (CONSENT_TEXT, with_back(consent_kb())),
    }
    return prompts[state]


ACC_PREV_STATE = {
    AcceleratorStates.waiting_for_name: ChoosingEvent.waiting_for_event,
    AcceleratorStates.waiting_for_project_name: AcceleratorStates.waiting_for_name,
    AcceleratorStates.waiting_for_email: AcceleratorStates.waiting_for_project_name,
    AcceleratorStates.waiting_for_tg: AcceleratorStates.waiting_for_email,
    AcceleratorStates.waiting_for_track: AcceleratorStates.waiting_for_tg,
    AcceleratorStates.waiting_for_stage: AcceleratorStates.waiting_for_track,
    AcceleratorStates.waiting_for_description: AcceleratorStates.waiting_for_stage,
    AcceleratorStates.waiting_for_pizzapitch: AcceleratorStates.waiting_for_description,
    AcceleratorStates.waiting_for_presentation_url: AcceleratorStates.waiting_for_pizzapitch,
    AcceleratorStates.waiting_for_team: AcceleratorStates.waiting_for_presentation_url,
    AcceleratorStates.waiting_for_hse: AcceleratorStates.waiting_for_team,
    AcceleratorStates.waiting_for_consent: AcceleratorStates.waiting_for_hse,
    AcceleratorStates.waiting_for_confirmation: AcceleratorStates.waiting_for_consent,
}

EV_PREV_STATE = {
    EventStates.waiting_for_name: ChoosingEvent.waiting_for_event,
    EventStates.waiting_for_hse: EventStates.waiting_for_name,
    EventStates.waiting_for_edu_program: EventStates.waiting_for_hse,
    EventStates.waiting_for_tg: EventStates.waiting_for_edu_program,
    EventStates.waiting_for_question: EventStates.waiting_for_tg,
    EventStates.waiting_for_consent: EventStates.waiting_for_question,
    EventStates.waiting_for_confirmation: EventStates.waiting_for_consent,
}


async def _show_event_choice(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ChoosingEvent.waiting_for_event)
    await callback.message.answer(
        "Выберите, на какое мероприятие хотите зарегистрироваться:",
        reply_markup=event_choice_kb(),
    )


@router.callback_query(F.data == "nav:back")
async def nav_back(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    current = await state.get_state()

    for step_state, prev_state in ACC_PREV_STATE.items():
        if current != step_state.state:
            continue
        if prev_state is ChoosingEvent.waiting_for_event:
            await _show_event_choice(callback, state)
            return
        await state.set_state(prev_state)
        text, markup = acc_step_prompt(prev_state)
        await callback.message.answer(text, reply_markup=markup)
        return

    for step_state, prev_state in EV_PREV_STATE.items():
        if current != step_state.state:
            continue
        if prev_state is ChoosingEvent.waiting_for_event:
            await _show_event_choice(callback, state)
            return
        await state.set_state(prev_state)
        text, markup = ev_step_prompt(prev_state)
        await callback.message.answer(text, reply_markup=markup)
        return

# --- /start и выбор мероприятия ---
WELCOME_TEXT = (
    "Привет! Этот бот создан для регистрации на мероприятия Бизнес-студии «ВоронаCreativeTech».\n\n"
    "Контакт для связи и поддержки: {support}"
)


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        WELCOME_TEXT.format(support=SUPPORT_USERNAME),
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        "Выберите, на какое мероприятие хотите зарегистрироваться:",
        reply_markup=event_choice_kb(),
    )
    await state.set_state(ChoosingEvent.waiting_for_event)


@router.callback_query(ChoosingEvent.waiting_for_event, F.data.in_(["ev:acc", "ev:evs"]))
async def process_event_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == "ev:acc":
        await state.update_data(event_type="accelerator")
        await state.set_state(AcceleratorStates.waiting_for_name)
        text, markup = acc_step_prompt(AcceleratorStates.waiting_for_name)
        await callback.message.answer(text, reply_markup=markup)
    else:
        await state.update_data(event_type="events")
        await state.set_state(EventStates.waiting_for_name)
        text, markup = ev_step_prompt(EventStates.waiting_for_name)
        await callback.message.answer(text, reply_markup=markup)


@router.message(ChoosingEvent.waiting_for_event)
async def wrong_event_choice(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Чтобы начать регистрацию, нажмите /start")


# ========== АКСЕЛЕРАТОР ==========
@router.message(AcceleratorStates.waiting_for_name, F.text)
async def acc_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await state.set_state(AcceleratorStates.waiting_for_project_name)
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_project_name)
    await message.answer(text, reply_markup=markup)


@router.message(AcceleratorStates.waiting_for_project_name, F.text)
async def acc_project(message: types.Message, state: FSMContext):
    await state.update_data(project_name=message.text.strip())
    await state.set_state(AcceleratorStates.waiting_for_email)
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_email)
    await message.answer(text, reply_markup=markup)


@router.message(AcceleratorStates.waiting_for_email, F.text)
async def acc_email(message: types.Message, state: FSMContext):
    if not validate_email(message.text):
        text, markup = acc_step_prompt(AcceleratorStates.waiting_for_email)
        await message.answer("Некорректный email. Введите снова:", reply_markup=markup)
        return
    await state.update_data(email=message.text.strip())
    await state.set_state(AcceleratorStates.waiting_for_tg)
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_tg)
    await message.answer(text, reply_markup=markup)


@router.message(AcceleratorStates.waiting_for_tg, F.text)
async def acc_tg(message: types.Message, state: FSMContext):
    if not validate_telegram_contact(message.text):
        text, markup = acc_step_prompt(AcceleratorStates.waiting_for_tg)
        await message.answer("Введите @username или номер телефона:", reply_markup=markup)
        return
    await state.update_data(contact=message.text.strip())
    await state.set_state(AcceleratorStates.waiting_for_track)
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_track)
    await message.answer(text, reply_markup=markup)


@router.callback_query(AcceleratorStates.waiting_for_track, F.data.startswith("tr:"))
async def acc_track(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    key = callback.data.split(":", 1)[1]
    if key not in ACCELERATOR_TRACKS:
        return
    await state.update_data(track=ACCELERATOR_TRACKS[key])
    await state.set_state(AcceleratorStates.waiting_for_stage)
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_stage)
    await callback.message.answer(text, reply_markup=markup)


@router.message(AcceleratorStates.waiting_for_track)
async def acc_track_wrong(message: types.Message):
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_track)
    await message.answer("Выберите направление кнопкой ниже.", reply_markup=markup)


@router.callback_query(AcceleratorStates.waiting_for_stage, F.data.startswith("st:"))
async def acc_stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    key = callback.data.split(":", 1)[1]
    if key not in ACCELERATOR_STAGES:
        return
    await state.update_data(stage=ACCELERATOR_STAGES[key])
    await state.set_state(AcceleratorStates.waiting_for_description)
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_description)
    await callback.message.answer(text, reply_markup=markup)


@router.message(AcceleratorStates.waiting_for_stage)
async def acc_stage_wrong(message: types.Message):
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_stage)
    await message.answer("Выберите этап кнопкой ниже.", reply_markup=markup)


@router.message(AcceleratorStates.waiting_for_description, F.text)
async def acc_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AcceleratorStates.waiting_for_pizzapitch)
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_pizzapitch)
    await message.answer(text, reply_markup=markup)


@router.callback_query(AcceleratorStates.waiting_for_pizzapitch, F.data.startswith("pz:"))
async def acc_pizzapitch(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    key = callback.data.split(":", 1)[1]
    if key not in PIZZAPITCH_CHOICES:
        return
    await state.update_data(pizzapitch=PIZZAPITCH_CHOICES[key])
    await state.set_state(AcceleratorStates.waiting_for_presentation_url)
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_presentation_url)
    await callback.message.answer(text, reply_markup=markup)


@router.message(AcceleratorStates.waiting_for_pizzapitch)
async def acc_pizzapitch_wrong(message: types.Message):
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_pizzapitch)
    await message.answer("Выберите вариант кнопкой ниже.", reply_markup=markup)


@router.message(AcceleratorStates.waiting_for_presentation_url, F.text)
async def acc_presentation(message: types.Message, state: FSMContext):
    if not validate_url(message.text):
        text, markup = acc_step_prompt(AcceleratorStates.waiting_for_presentation_url)
        await message.answer("Введите корректную ссылку (http:// или https://):", reply_markup=markup)
        return
    await state.update_data(presentation_url=message.text.strip())
    await state.set_state(AcceleratorStates.waiting_for_team)
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_team)
    await message.answer(text, reply_markup=markup)


@router.message(AcceleratorStates.waiting_for_team, F.text)
async def acc_team(message: types.Message, state: FSMContext):
    await state.update_data(team=message.text.strip())
    await state.set_state(AcceleratorStates.waiting_for_hse)
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_hse)
    await message.answer(text, reply_markup=markup)


@router.callback_query(AcceleratorStates.waiting_for_hse, F.data.in_(["yn:y", "yn:n"]))
async def acc_hse(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(hse="Да" if callback.data == "yn:y" else "Нет")
    await state.set_state(AcceleratorStates.waiting_for_consent)
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_consent)
    await callback.message.answer(text, reply_markup=markup)


@router.message(AcceleratorStates.waiting_for_hse)
async def acc_hse_wrong(message: types.Message):
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_hse)
    await message.answer("Выберите «Да» или «Нет» кнопкой ниже.", reply_markup=markup)


@router.callback_query(AcceleratorStates.waiting_for_consent, F.data == "consent")
async def acc_consent(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    summary = (
        "Проверьте данные:\n\n"
        f"ФИО: {data['full_name']}\n"
        f"Название проекта: {data['project_name']}\n"
        f"Email: {data['email']}\n"
        f"Тг: {data['contact']}\n"
        f"Направление: {data['track']}\n"
        f"Этап: {data['stage']}\n"
        f"Описание: {data['description'][:100]}{'…' if len(data['description']) > 100 else ''}\n"
        f"PizzaPitch/Прожарка: {data['pizzapitch']}\n"
        f"Ссылка на презентацию: {data['presentation_url']}\n"
        f"Команда: {data['team'][:80]}{'…' if len(data['team']) > 80 else ''}\n"
        f"Вы из ВШЭ: {data['hse']}\n\n"
        "Всё верно?"
    )
    await state.set_state(AcceleratorStates.waiting_for_confirmation)
    await callback.message.answer(summary, reply_markup=with_back(confirm_kb()))


@router.message(AcceleratorStates.waiting_for_consent)
async def acc_consent_wrong(message: types.Message):
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_consent)
    await message.answer("Нажмите «Да, я ознакомился» под сообщением выше.", reply_markup=markup)


@router.callback_query(AcceleratorStates.waiting_for_confirmation, F.data == "conf:y")
async def acc_confirm_yes(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    data["user_id"] = callback.from_user.id
    data["registration_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_name = EVENTS["accelerator"]
    if sheets_service.save_registration("accelerator", data):
        await callback.message.answer(
            f"Регистрация на {event_name} завершена. 🎉\n\n"
            "Если хотите зарегистрироваться ещё раз или на второе мероприятие, нажмите /start",
        )
        await _notify_admins(callback.bot, "Акселератор", data)
    else:
        await callback.message.answer(
            "Ошибка при сохранении. Попробуйте позже или нажмите /start.",
        )
    await state.clear()


@router.callback_query(AcceleratorStates.waiting_for_confirmation, F.data == "conf:e")
async def acc_confirm_edit(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AcceleratorStates.waiting_for_name)
    text, markup = acc_step_prompt(AcceleratorStates.waiting_for_name)
    await callback.message.answer(text, reply_markup=markup)


@router.message(AcceleratorStates.waiting_for_confirmation)
async def acc_confirm_wrong(message: types.Message):
    await message.answer(
        "Нажмите «✅ Да» или «✏️ Изменить» под сообщением с данными.",
        reply_markup=with_back(confirm_kb()),
    )


# ========== МЕРОПРИЯТИЯ ==========
@router.message(EventStates.waiting_for_name, F.text)
async def ev_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await state.set_state(EventStates.waiting_for_hse)
    text, markup = ev_step_prompt(EventStates.waiting_for_hse)
    await message.answer(text, reply_markup=markup)


@router.callback_query(EventStates.waiting_for_hse, F.data.in_(["yn:y", "yn:n"]))
async def ev_hse(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(hse="Да" if callback.data == "yn:y" else "Нет")
    await state.set_state(EventStates.waiting_for_edu_program)
    text, markup = ev_step_prompt(EventStates.waiting_for_edu_program)
    await callback.message.answer(text, reply_markup=markup)


@router.message(EventStates.waiting_for_hse)
async def ev_hse_wrong(message: types.Message):
    text, markup = ev_step_prompt(EventStates.waiting_for_hse)
    await message.answer("Выберите «Да» или «Нет» кнопкой ниже.", reply_markup=markup)


@router.message(EventStates.waiting_for_edu_program, F.text)
async def ev_edu(message: types.Message, state: FSMContext):
    await state.update_data(edu_program=message.text.strip())
    await state.set_state(EventStates.waiting_for_tg)
    text, markup = ev_step_prompt(EventStates.waiting_for_tg)
    await message.answer(text, reply_markup=markup)


@router.message(EventStates.waiting_for_tg, F.text)
async def ev_tg(message: types.Message, state: FSMContext):
    if not validate_telegram_contact(message.text):
        text, markup = ev_step_prompt(EventStates.waiting_for_tg)
        await message.answer("Введите @username или номер телефона:", reply_markup=markup)
        return
    await state.update_data(contact=message.text.strip())
    await state.set_state(EventStates.waiting_for_question)
    text, markup = ev_step_prompt(EventStates.waiting_for_question)
    await message.answer(text, reply_markup=markup)


@router.message(EventStates.waiting_for_question, F.text)
async def ev_question(message: types.Message, state: FSMContext):
    text = message.text.strip()
    await state.update_data(question="-" if text == "-" else text)
    await state.set_state(EventStates.waiting_for_consent)
    text, markup = ev_step_prompt(EventStates.waiting_for_consent)
    await message.answer(text, reply_markup=markup)


@router.callback_query(EventStates.waiting_for_consent, F.data == "consent")
async def ev_consent(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    summary = (
        "Проверьте данные:\n\n"
        f"ФИО: {data['full_name']}\n"
        f"Вы из ВШЭ: {data['hse']}\n"
        f"Образовательная программа: {data.get('edu_program', '')}\n"
        f"Тг: {data['contact']}\n"
        f"Вопрос: {data.get('question', '-')}\n\n"
        "Всё верно?"
    )
    await state.set_state(EventStates.waiting_for_confirmation)
    await callback.message.answer(summary, reply_markup=with_back(confirm_kb()))


@router.message(EventStates.waiting_for_consent)
async def ev_consent_wrong(message: types.Message):
    text, markup = ev_step_prompt(EventStates.waiting_for_consent)
    await message.answer("Нажмите «Да, я ознакомился» под сообщением выше.", reply_markup=markup)


@router.callback_query(EventStates.waiting_for_confirmation, F.data == "conf:y")
async def ev_confirm_yes(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    data["user_id"] = callback.from_user.id
    data["registration_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_name = EVENTS["events"]
    if sheets_service.save_registration("events", data):
        await callback.message.answer(
            f"Регистрация на {event_name} завершена. 🎉\n\n"
            "Если хотите зарегистрироваться ещё раз или на второе мероприятие, нажмите /start",
        )
        await _notify_admins(callback.bot, "Мероприятия", data)
    else:
        await callback.message.answer(
            "Ошибка при сохранении. Попробуйте позже или нажмите /start.",
        )
    await state.clear()


@router.callback_query(EventStates.waiting_for_confirmation, F.data == "conf:e")
async def ev_confirm_edit(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(EventStates.waiting_for_name)
    text, markup = ev_step_prompt(EventStates.waiting_for_name)
    await callback.message.answer(text, reply_markup=markup)


@router.message(EventStates.waiting_for_confirmation)
async def ev_confirm_wrong(message: types.Message):
    await message.answer(
        "Нажмите «✅ Да» или «✏️ Изменить» под сообщением с данными.",
        reply_markup=with_back(confirm_kb()),
    )


async def _notify_admins(bot, event_label: str, data: dict):
    text = f"Новая регистрация ({event_label})\n\nФИО: {data.get('full_name')}\nТг: {data.get('contact')}"
    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")
