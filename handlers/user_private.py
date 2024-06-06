from aiogram import F, types, Router
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_add_to_cart, orm_add_user
from filters.chat_types import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from kbds.inline import MenuCallBack


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))  # Сообщения которые работают в боте


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main") # Получаем изображение и клавиатуру
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


async def add_to_cart(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = callback.from_user # Получаем id
    await orm_add_user( 
        session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None,
    ) # Добавляем его в БД
    await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id) # Добавить товар в корзину
    await callback.answer("Товар добавлен в корзину.")


@user_private_router.callback_query(MenuCallBack.filter()) # Фильтр по префиксу
async def user_menu(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    if callback_data.menu_name == "add_to_cart":
        await add_to_cart(callback, callback_data, session)
        return
    media, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        user_id=callback.from_user.id,
    )
    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()