# АРХИТЕКТУРА И СПЕЦИФИКАЦИЯ ПРОЕКТА: 808 VAULT

> **Проект:** 808 Vault — Студия звукозаписи и маркетплейс битов  
> **Клиент / Заказчик:** 808 Vault Sound Lab (@808vault_studio)  
> **Чек проекта:** 140,000 ₽ | **Срок:** 14 дней (Дедлайн: 2026-11-25)  
> **Дедлайн MVP (80%):** 2026-11-22  
> **Тип договора:** Договор СМЗ с ИП (Чек «Мой Налог»)

---

## 🛠 Технологический стек
- **Frontend / UI:** Vanilla JS / HTML5 Web Audio API, Canvas Waveform Visualizer, Modern CSS (DAW Dark Theme #141518 / #1E1F24, VU Meters, Channel Strips)
- **Backend / Web API:** Python 3.12, FastAPI, Uvicorn, Pydantic v2
- **Telegram Bot:** Python 3.12, Aiogram 3.x, FSM (Finite State Machine), Inline Keyboards
- **Аудио-технологии:** Web Audio API GainNodes, Dual-Buffer Synchronous Playback, Synthesized & Real Audio Streams
- **Хранилище данных:** In-Memory State & JSON Catalog with Lead Notification Dispatch

---

## 🏛 Архитектурная схема
```
[ Музыкант / Продюсер ] 
          │ 
          ├──────────────► [ Веб-интерфейс DAW (Порт 3016) ]
          │                  - Синхронный A/B плеер (Raw vs Mastered)
          │                  - DAW Mixer с фейдерами и LED VU-метрами
          │                  - Селектор лицензий и бронирование студии
          │                  - REST API /api/tracks, /api/licenses, /api/book-session
          │
          └──────────────► [ Telegram-бот @Vault808Bot ]
                             - Сниппеты битов и лицензирование (WAV, Trackout, Exclusive)
                             - FSM бронирования студийных сессий
                             - Диспетчер лидов в @Idrisov_prod
```

---

## 🔐 Переменные окружения (.env.example)
```env
BOT_TOKEN=8217851677:AAHN34TMuC1P4e6SppuazFN8BIiLHa_RyIc
TELEGRAM_OWNER_ID=1387913438
TELEGRAM_OWNER_USERNAME=@Idrisov_prod
PORT=3016
API_PORT=8016
WEBHOOK_URL=http://localhost:8016/webhook
```

---

## 🔗 Ресурсы и ссылки
- **Порт Web/API:** `3016` (Web UI), `8016` (API)
- **Telegram Bot:** `@Vault808Bot`
- **Код проекта:** `C:\Users\danie\OneDrive\Desktop\Idrisov\Idrisov_OS\01_Business\Projects\Case16_808Vault\`
