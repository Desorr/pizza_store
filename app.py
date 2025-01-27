import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.admin_private import admin_router
#from handlers.payments import pay_router
from handlers.payments_redsys import pay_redsys_router


bot = Bot(token=os.getenv("TOKEN"), parse_mode=ParseMode.HTML)
bot.my_admins_list = [] # Список админов

dp = Dispatcher()

dp.include_router(user_private_router)  
dp.include_router(user_group_router)  
dp.include_router(admin_router)
#dp.include_router(pay_router)
dp.include_router(pay_redsys_router)

# Запуск бота
async def on_startup(bot):
    # await drop_db() # Удалить БД
    await create_db() # Создать БД

# При выключении бота
async def on_shutdown(bot):
    print('бот лег')

async def main():
    dp.startup.register(on_startup) # При включении бота вызвать функцию
    dp.shutdown.register(on_shutdown) # При выключении бота вызвать функцию
    dp.update.middleware(DataBaseSession(session_pool=session_maker)) # В каждый хэндлер пробрасывается сессия
    await bot.delete_webhook(drop_pending_updates=True) # Скипнуть апйдейты, когда бот не работал
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()) # Запускает бота в работу, бот слушает сервер о наличии обновлений, у нас определенные - допустимые


asyncio.run(main())
