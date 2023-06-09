# telegram chess bot

[![Discourse topics](https://img.shields.io/badge/telegram-%40pvp__chessbot-blue)](https://t.me/pvp_chessbot) [![Discourse topics](https://img.shields.io/badge/License-GPLv3-orange)](https://www.gnu.org/licenses/gpl-3.0) 

### Бот позволяющий играть в шахматы с людьми либо с шахматным движком по стандартным правилам при помощи инлайн клавиатуры.

![image](https://github.com/pulivilizator/ChessBot/assets/112427972/50d680a8-efd9-4ecf-9800-4dd82827d9e3)

### Используемые технологии:
- Python 3.11;
- aiogram 3;
- Redis (хранилище для машины состояний)(В разработке);
- PostgresSQL(Для хранений данных пользователей)(В разработке)
---
### Установка и настройка:

Бот тестировался на Ubuntu 22.04.

- Для игры с ботом скачайте шахматный движок под Вашу систему, бот использовался с [Stockfish](https://stockfishchess.org/download/).
- Клонируйте проект: `git clone https://github.com/pulivilizator/ChessBot.git`
- Создайте и активируйте виртуальное окружение: `python3 -m venv venv` `source venv/bin/activate`
- Установите pip и зависимости `sudo apt install pip` `pip install -r requirements.txt`
- Установите доп. пакеты `sudo apt install libcairo2 libcairo2-dev`
- Переименуйте .env.example в .env, и укажите токен своего бота
- Укажите путь к движку в файле */bot/chess_engine/chess_with_bot/engine_game.py*
- Перейдите в папку с ботом, и запустите его: `cd bot` `python3 bot.py`
