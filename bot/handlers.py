from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards import (
    get_main_keyboard,
    get_beats_inline_kb,
    get_license_options_kb,
    get_studio_rooms_kb,
    get_time_slots_kb
)
from bot.config import TELEGRAM_OWNER_ID, TELEGRAM_OWNER_USERNAME

router = Router()

class StudioBookingFSM(StatesGroup):
    room = State()
    date = State()
    time_slot = State()
    client_name = State()
    client_contact = State()

TRACKS_DATA = {
    "trk-01": {"title": "Sub Zero 808", "bpm": 140, "key": "D Minor", "genre": "Dark Trap"},
    "trk-02": {"title": "Cyber Drift Phonk", "bpm": 160, "key": "F# Minor", "genre": "Memphis Phonk"},
    "trk-03": {"title": "Phantom Drill", "bpm": 142, "key": "C Minor", "genre": "UK Drill"},
    "trk-04": {"title": "Neon Syndicate", "bpm": 128, "key": "A Minor", "genre": "Cyberpunk Synthwave"}
}

@router.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "🎛 **ДОБРО ПОЖАЛОВАТЬ В 808 VAULT SOUND LAB**\n\n"
        "Студия звукозаписи полного цикла и маркетплейс эксклюзивных битов.\n\n"
        "⚡ Здесь ты можешь:\n"
        "— Прослушать сниппеты свежих битов в высоком качестве\n"
        "— Приобрести коммерческую лицензию (WAV Lease / Stems / Exclusive)\n"
        "— Забронировать смену записи на студии (Vocal Booth / Control Room)\n\n"
        "Используй меню ниже для навигации:"
    )
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@router.message(F.text == "🎵 Витрина битов")
async def show_beats_catalog(message: Message):
    text = (
        "🔥 **КАТАЛОГ СВЕЖИХ БИТОВ 808 VAULT**\n"
        "Выбери интересующий трек для подробностей и лицензирования:"
    )
    await message.answer(text, reply_markup=get_beats_inline_kb(), parse_mode="Markdown")

@router.callback_query(F.data.startswith("beat_"))
async def handle_beat_selection(callback: CallbackQuery):
    track_id = callback.data.replace("beat_", "")
    track = TRACKS_DATA.get(track_id)
    if not track:
        await callback.answer("Трек не найден", show_alert=True)
        return

    text = (
        f"🎧 **ТРЕК: {track['title']}**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎹 Тональность: `{track['key']}`\n"
        f"🥁 Темп: `{track['bpm']} BPM`\n"
        f"🏷 Жанр: `{track['genre']}`\n"
        f"🔊 Сведение: SSL Analog Console + Tube Saturator\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Выбери тип лицензии для покупки:"
    )
    await callback.message.edit_text(text, reply_markup=get_license_options_kb(track_id), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "back_to_beats")
async def handle_back_to_beats(callback: CallbackQuery):
    text = "🔥 **КАТАЛОГ СВЕЖИХ БИТОВ 808 VAULT**\nВыбери трек для прослушивания:"
    await callback.message.edit_text(text, reply_markup=get_beats_inline_kb(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("lic_"))
async def handle_license_checkout(callback: CallbackQuery):
    parts = callback.data.split("_")
    lic_code = parts[1]
    track_id = parts[2]
    track = TRACKS_DATA.get(track_id, {"title": "Unknown Track"})

    lic_names = {
        "wav": ("WAV Lease", "3 000 ₽", "Lossless WAV, до 50k стримов"),
        "stems": ("Trackout Stems", "8 500 ₽", "Подорожечные стемы WAV для студийного сведения"),
        "excl": ("Exclusive Rights", "35 000 ₽", "Полное отчуждение прав, снятие с продажи")
    }

    name, price, desc = lic_names.get(lic_code, ("Стандартная лицензия", "3 000 ₽", "WAV"))

    text = (
        f"✅ **ОФОРМЛЕНИЕ ЛИЦЕНЗИИ**\n\n"
        f"📦 Трек: **{track['title']}**\n"
        f"📜 Тип: **{name}**\n"
        f"💰 Стоимость: **{price}**\n"
        f"ℹ Условия: {desc}\n\n"
        f"Менеджер студии {TELEGRAM_OWNER_USERNAME} подготовит персональный договор и ссылку на скачивание архива.\n"
        f"Подтверждаешь заказ?"
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer("Заявка зарегистрирована!")

@router.message(F.text == "📜 Лицензии и права")
async def show_license_info(message: Message):
    text = (
        "📜 **ТИПЫ ЛИЦЕНЗИЙ 808 VAULT**\n\n"
        "1. **MP3 Lease (1 500 ₽)** — 320 kbps MP3, лимит 5 000 стримов, некоммерческое использование.\n"
        "2. **WAV Lease (3 000 ₽)** — 24-bit WAV, до 50 000 стримов, монетизация в стримингах.\n"
        "3. **Trackout Stems (8 500 ₽)** — раздельные стемы (WAV), до 500 000 стримов, полная свобода сведения.\n"
        "4. **Exclusive Rights (35 000 ₽)** — безлимитные права, трек снимается с витрины навсегда, официальный договор."
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "🎙 Запись на студию")
async def start_studio_booking(message: Message, state: FSMContext):
    await state.set_state(StudioBookingFSM.room)
    await message.answer(
        "🎙 **БРОНИРОВАНИЕ СТУДИЙНОЙ СЕССИИ**\n\n"
        "Шаг 1 из 5: Выбери студийное помещение:",
        reply_markup=get_studio_rooms_kb(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("room_"), StudioBookingFSM.room)
async def process_room_choice(callback: CallbackQuery, state: FSMContext):
    rooms = {
        "room_vocal": "Vocal Booth (Neumann U87)",
        "room_control": "Main Control Room (Barefoot MM27)",
        "room_atmos": "Dolby Atmos 7.1.4 Mixing Suite"
    }
    selected_room = rooms.get(callback.data, "Vocal Booth")
    await state.update_data(room=selected_room)
    await state.set_state(StudioBookingFSM.date)
    await callback.message.edit_text(
        f"Выбрана студия: **{selected_room}**\n\n"
        f"Шаг 2 из 5: Введи желаемую дату сессии (например: `2026-11-20` или `Завтра`):",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(StudioBookingFSM.date)
async def process_booking_date(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(StudioBookingFSM.time_slot)
    await message.answer(
        "Шаг 3 из 5: Выбери временной слот сессии:",
        reply_markup=get_time_slots_kb()
    )

@router.callback_query(F.data.startswith("slot_"), StudioBookingFSM.time_slot)
async def process_time_slot(callback: CallbackQuery, state: FSMContext):
    slots = {
        "slot_12_15": "12:00 - 15:00 (Дневной, 3h)",
        "slot_15_19": "15:30 - 19:30 (Прайм, 4h)",
        "slot_20_02": "20:00 - 02:00 (Ночной лок-ин, 6h)"
    }
    selected_slot = slots.get(callback.data, "15:30 - 19:30")
    await state.update_data(time_slot=selected_slot)
    await state.set_state(StudioBookingFSM.client_name)
    await callback.message.edit_text(
        f"Выбран слот: **{selected_slot}**\n\n"
        f"Шаг 4 из 5: Как к тебе обращаться (Имя / Никнейм артиста)?",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(StudioBookingFSM.client_name)
async def process_client_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(StudioBookingFSM.client_contact)
    await message.answer(
        "Шаг 5 из 5: Оставь контактный номер телефона или Telegram-юзернейм для подтверждения брони:"
    )

@router.message(StudioBookingFSM.client_contact)
async def process_client_contact(message: Message, state: FSMContext):
    data = await state.get_data()
    contact = message.text
    await state.clear()

    summary_text = (
        "🎉 **ВАША ЗАЯВКА НА СТУДИЮ УСПЕШНО ОФОРМЛЕНА!**\n\n"
        f"📍 Комната: **{data.get('room')}**\n"
        f"📅 Дата: **{data.get('date')}**\n"
        f"⏰ Слот: **{data.get('time_slot')}**\n"
        f"👤 Артист: **{data.get('name')}**\n"
        f"📞 Контакт: **{contact}**\n\n"
        f"Звукорежиссер студии свяжется с вами в течение 15 минут для подтверждения брони!"
    )
    await message.answer(summary_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@router.message(F.text == "ℹ О студии 808 Vault")
async def show_studio_about(message: Message):
    text = (
        "🏢 **808 VAULT SOUND LAB // MOSCOW**\n\n"
        "• Мониторинг: Barefoot MicroMain27, Yamaha NS-10M Studio, Genelec 8351B\n"
        "• Преампы и компрессоры: Avalon VT-737sp, Tube-Tech CL1B, Universal Audio 1176LN\n"
        "• Микрофоны: Neumann U87 Ai, Sony C-800G, Shure SM7B\n"
        "• Локация: г. Москва, ул. Звукорежиссерская, 8\n"
        "• Менеджер студии: @Idrisov_prod"
    )
    await message.answer(text, parse_mode="Markdown")
