import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())  # Автоматически находит и подгружает переменные из файла .env

from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.admin_private import admin_router


bot = Bot(token=os.getenv("TOKEN"), parse_mode=ParseMode.HTML)  # Инициализация бота и добавить форматировать текст в боте
bot.my_admins_list = [] # Список админов

dp = Dispatcher()  # Данный класс принимает и обрабатывает все апдейты

dp.include_router(user_private_router)  # Подключаем роутеры с хэндлеров бот
dp.include_router(user_group_router)  # Подключаем роутеры с хэндлеров группа
dp.include_router(admin_router) # Подключаем роутеры с хэндлеров админа бот

async def on_startup(bot): # При запуске бота
    # await drop_db() # Удалить БД
    await create_db() # Создать БД


async def on_shutdown(bot): # При выключении бота
    print('бот лег')


async def main():
    dp.startup.register(on_startup) # При включении бота вызвать функцию
    dp.shutdown.register(on_shutdown) # При выключении бота вызвать функцию
    dp.update.middleware(DataBaseSession(session_pool=session_maker)) # В каждый хэндлер пробрасывается сессия
    await bot.delete_webhook(drop_pending_updates=True) # Скипнуть апйдейты, когда бот не работал
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()) # Запускает бота в работу, бот слушает сервер о наличии обновлений, у нас определенные - допустимые


asyncio.run(main())  # Запуск
