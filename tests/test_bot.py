import pytest
from aiogram import Router
from bot.handlers import router, StudioBookingFSM, TRACKS_DATA
from bot.keyboards import (
    get_main_keyboard,
    get_beats_inline_kb,
    get_license_options_kb,
    get_studio_rooms_kb,
    get_time_slots_kb
)

def test_router_registration():
    assert isinstance(router, Router)
    assert len(router.message.handlers) >= 5
    assert len(router.callback_query.handlers) >= 4

def test_keyboards_structure():
    main_kb = get_main_keyboard()
    assert len(main_kb.keyboard) >= 2
    button_texts = [btn.text for row in main_kb.keyboard for btn in row]
    assert "🎵 Витрина битов" in button_texts
    assert "🎙 Запись на студию" in button_texts

    beats_kb = get_beats_inline_kb()
    assert len(beats_kb.inline_keyboard) == 4
    assert beats_kb.inline_keyboard[0][0].callback_data == "beat_trk-01"

    lic_kb = get_license_options_kb("trk-01")
    assert len(lic_kb.inline_keyboard) == 4
    assert "lic_wav_trk-01" in lic_kb.inline_keyboard[0][0].callback_data

    rooms_kb = get_studio_rooms_kb()
    assert len(rooms_kb.inline_keyboard) == 3

    slots_kb = get_time_slots_kb()
    assert len(slots_kb.inline_keyboard) == 3

def test_fsm_states_definition():
    assert hasattr(StudioBookingFSM, "room")
    assert hasattr(StudioBookingFSM, "date")
    assert hasattr(StudioBookingFSM, "time_slot")
    assert hasattr(StudioBookingFSM, "client_name")
    assert hasattr(StudioBookingFSM, "client_contact")

def test_tracks_data_integrity():
    assert "trk-01" in TRACKS_DATA
    assert TRACKS_DATA["trk-01"]["bpm"] == 140
    assert TRACKS_DATA["trk-01"]["key"] == "D Minor"
