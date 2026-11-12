from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🎵 Витрина битов"), KeyboardButton(text="📜 Лицензии и права")],
        [KeyboardButton(text="🎙 Запись на студию"), KeyboardButton(text="ℹ О студии 808 Vault")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_beats_inline_kb() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="▶ Sub Zero 808 (140 BPM, Dm)", callback_data="beat_trk-01"),
        ],
        [
            InlineKeyboardButton(text="▶ Cyber Drift Phonk (160 BPM, F#m)", callback_data="beat_trk-02"),
        ],
        [
            InlineKeyboardButton(text="▶ Phantom Drill (142 BPM, Cm)", callback_data="beat_trk-03"),
        ],
        [
            InlineKeyboardButton(text="▶ Neon Syndicate (128 BPM, Am)", callback_data="beat_trk-04"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_license_options_kb(track_id: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="💿 WAV Lease — 3 000 ₽", callback_data=f"lic_wav_{track_id}")],
        [InlineKeyboardButton(text="🎚 Trackout Stems — 8 500 ₽", callback_data=f"lic_stems_{track_id}")],
        [InlineKeyboardButton(text="👑 Exclusive Rights — 35 000 ₽", callback_data=f"lic_excl_{track_id}")],
        [InlineKeyboardButton(text="« Назад в каталог", callback_data="back_to_beats")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_studio_rooms_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🎙 Vocal Booth (Neumann U87)", callback_data="room_vocal")],
        [InlineKeyboardButton(text="🎛 Main Control Room (Barefoot)", callback_data="room_control")],
        [InlineKeyboardButton(text="🔊 Dolby Atmos 7.1.4 Suite", callback_data="room_atmos")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_time_slots_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="12:00 - 15:00 (Дневной)", callback_data="slot_12_15")],
        [InlineKeyboardButton(text="15:30 - 19:30 (Прайм-сессия)", callback_data="slot_15_19")],
        [InlineKeyboardButton(text="20:00 - 02:00 (Ночной лок-ин)", callback_data="slot_20_02")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
