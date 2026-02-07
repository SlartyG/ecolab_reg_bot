from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.states import AdminStates
from services.sheets import GoogleSheetsService
from config import ADMINS

router = Router()
sheets_service = GoogleSheetsService()

broadcast_messages = {}

def is_admin(message: types.Message) -> bool:
    return message.from_user.id in ADMINS

def is_admin_callback(callback: types.CallbackQuery) -> bool:
    return callback.from_user.id in ADMINS

# Аудитории рассылки (callback_data — короткие из-за лимита 64 байта)
AUDIENCE_ALL = "Всем (Акселератор + Мероприятия)"
AUDIENCE_ACCELERATOR = "Зарегистрированные на Акселератор"
AUDIENCE_EVENTS = "Зарегистрированные на Мероприятия"

def audience_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=AUDIENCE_ALL, callback_data="aud:all")],
        [InlineKeyboardButton(text=AUDIENCE_ACCELERATOR, callback_data="aud:acc")],
        [InlineKeyboardButton(text=AUDIENCE_EVENTS, callback_data="aud:ev")],
        [InlineKeyboardButton(text="Отменить рассылку", callback_data="aud:can")],
    ])

def broadcast_cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить рассылку", callback_data="bc:can")],
    ])


@router.message(Command("send"), is_admin)
async def cmd_send(message: types.Message, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_audience)
    await message.answer(
        "Выберите аудиторию рассылки:",
        reply_markup=audience_kb(),
    )


@router.callback_query(AdminStates.waiting_for_audience, F.data.startswith("aud:"))
async def process_audience(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin_callback(callback):
        await callback.answer("Нет прав.", show_alert=True)
        await state.clear()
        return

    if callback.data == "aud:can":
        await callback.answer()
        await state.clear()
        await callback.message.answer("Рассылка отменена.")
        return

    if callback.data not in ("aud:all", "aud:acc", "aud:ev"):
        await callback.answer()
        return

    await callback.answer()
    audience_map = {"aud:all": "all", "aud:acc": "accelerator", "aud:ev": "events"}
    await state.update_data(audience=audience_map[callback.data])
    await state.set_state(AdminStates.waiting_for_broadcast)
    await callback.message.answer(
        "Введите текст рассылки:",
        reply_markup=broadcast_cancel_kb(),
    )


@router.message(AdminStates.waiting_for_audience)
async def wrong_audience(message: types.Message):
    await message.answer("Используйте кнопки выше для выбора аудитории.", reply_markup=audience_kb())


@router.callback_query(AdminStates.waiting_for_broadcast, F.data == "bc:can")
async def broadcast_cancel(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin_callback(callback):
        await callback.answer("Нет прав.", show_alert=True)
        return
    await callback.answer()
    await state.clear()
    await callback.message.answer("Рассылка отменена.")


@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    if not is_admin(message):
        await message.answer("Нет прав.")
        await state.clear()
        return

    data = await state.get_data()
    audience_key = data.get("audience", "all")
    user_ids = sheets_service.get_user_ids(audience_key)

    if not user_ids:
        await message.answer(
            "Нет пользователей в выбранной аудитории для рассылки.",
        )
        await state.clear()
        return

    sent_messages = []
    for user_id in user_ids:
        try:
            sent_msg = await message.bot.send_message(user_id, message.text)
            sent_messages.append({"user_id": user_id, "message_id": sent_msg.message_id})
        except Exception as e:
            print(f"Error sending to {user_id}: {e}")

    broadcast_messages[message.message_id] = sent_messages
    stats = (
        "Рассылка завершена!\n\n"
        f"✅ Отправлено: {len(sent_messages)} сообщений\n"
        "Чтобы удалить это сообщение у всех, удалите его и ответьте /delete."
    )
    sent_stat = await message.answer(stats)
    broadcast_messages[sent_stat.message_id] = sent_messages
    await state.clear()


@router.message(F.text == "/delete")
async def handle_message_deletion(message: types.Message):
    if not is_admin(message):
        await message.answer("Нет прав.")
        return
    if not message.reply_to_message:
        await message.answer("Ответьте на сообщение рассылки, которое нужно удалить у всех.")
        return
    reply_msg_id = message.reply_to_message.message_id
    if reply_msg_id not in broadcast_messages:
        await message.answer("Это не сообщение рассылки.")
        return
    sent_messages = broadcast_messages[reply_msg_id]
    deleted_count = 0
    error_count = 0
    for msg in sent_messages:
        try:
            await message.bot.delete_message(msg["user_id"], msg["message_id"])
            deleted_count += 1
        except Exception as e:
            print(f"Error deleting for {msg['user_id']}: {e}")
            error_count += 1
    del broadcast_messages[reply_msg_id]
    await message.answer(
        f"Удалено: {deleted_count}, ошибок: {error_count}",
    )
