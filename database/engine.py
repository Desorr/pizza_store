import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import Base
from database.orm_query import orm_add_banner_description, orm_create_categories
from common.texts_for_db import categories, description_for_info_pages


# from .env file:
# DB_LITE=sqlite+aiosqlite:///my_base.db
# DB_URL=postgresql+asyncpg://login:password@localhost:5432/db_name
# engine = create_async_engine(os.getenv('DB_LITE'), echo=True)

engine = create_async_engine(os.getenv('DB_URL'), echo=True) # Подтягиваем базу данных по url из .env и echo-вывод в терминал всех sql-запросов которые создаются 

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False) # Берем сессии, чтобы делать запросы в БД. bind-подвязываем движок, expire_on_commit-воспользоваться сессией повторно после commit(чтобы не закрывалась)


async def create_db(): # Создать все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # Создать все таблицы
    async with session_maker() as session:
        await orm_create_categories(session, categories) # Создать все категории
        await orm_add_banner_description(session, description_for_info_pages) # Добавить описание для баннеров


async def drop_db(): # Удалить все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # Удалить все таблицы