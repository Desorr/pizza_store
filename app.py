import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.admin_private import admin_router
from handlers.payment_redsys import pay_redsys_router


bot = Bot(token=os.getenv("TOKEN"))
bot.my_admins_list = [] # Список админов

dp = Dispatcher()

dp.include_router(user_private_router)
dp.include_router(user_group_router)
dp.include_router(admin_router)
dp.include_router(pay_redsys_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await drop_db() # Удалить БД
    await create_db()  # Создать БД
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    webhook_url = os.getenv("WEBHOOK_URL")

    await bot.delete_webhook(drop_pending_updates=True)

    await bot.set_webhook(f"{webhook_url}/webhook")
    yield
    print("Остановка бота...")
    await bot.delete_webhook(drop_pending_updates=True)

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def handle_webhook(update: Update):
    await dp.feed_update(bot, update)
    return {"status": "ok"}
