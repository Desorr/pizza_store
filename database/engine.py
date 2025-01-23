import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import Base
from database.orm_query import orm_add_banner_description, orm_create_categories
from common.texts_for_db import categories, description_for_info_pages
from utils.banner_change import prepare_banner_data


# from .env file:
# DB_LITE=sqlite+aiosqlite:///my_base.db
# DB_URL=postgresql+asyncpg://login:password@localhost:5432/db_name
# engine = create_async_engine(os.getenv('DB_LITE'), echo=True)

engine = create_async_engine(os.getenv('DB_URL'), echo=True) # Подтягиваем базу данных по url из .env и echo-вывод в терминал всех sql-запросов которые создаются 

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False) # Берем сессии, чтобы делать запросы в БД. bind-подвязываем движок, expire_on_commit-воспользоваться сессией повторно после commit(чтобы не закрывалась)


# Создать все таблицы, добавить категории и описание к баннерам
async def create_db(): 
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with session_maker() as session:
        await orm_create_categories(session, categories)
        banner_data_list = prepare_banner_data(description_for_info_pages)
        for banner_data in banner_data_list:
            await orm_add_banner_description(session, banner_data)

# Удалить все таблицы
async def drop_db(): 
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)