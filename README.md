# Бот для психо- и нейролингвистических экспериментов

Telegram-бот для проведения психо- и нейролингвистических
экспериментов и сбора данных от информантов. ВКР, НИУ ВШЭ, ОП
«Фундаментальная и компьютерная лингвистика», 2026.

Документация: [`./docs/`](./docs/) или
`https://mayyagorsh.github.io/LingExp_bot`.

## Локальный запуск

1. Создать `.env` в корне со значениями:

   ```
   BOT_TOKEN=...
   MONGO_URI=mongodb://localhost:27017
   DB_NAME=linguistic_bot
   ```

2. `pip install -r requirements.txt`.
3. `python -m bot.main`.
