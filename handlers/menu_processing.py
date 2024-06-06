from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import (
    orm_add_to_cart,
    orm_delete_from_cart,
    orm_get_banner,
    orm_get_categories,
    orm_get_products,
    orm_get_user_carts,
    orm_reduce_product_in_cart,
)
from kbds.inline import get_products_btns, get_user_cart, get_user_catalog_btns, get_user_main_btns
from utils.paginator import Paginator


async def main_menu(session, level, menu_name): # Lvl 0 и все что с ним должно выводиться 
    banner = await orm_get_banner(session, menu_name) # Получить баннер
    image = InputMediaPhoto(media=banner.image, caption=banner.description) # Передаем баннер и описание
    kbds = get_user_main_btns(level=level) # Клавиатура на Lvl 0
    return image, kbds


async def catalog(session, level, menu_name): # Lvl 1 и все что с ним должно выводиться 
    banner = await orm_get_banner(session, menu_name) # Получить баннер
    image = InputMediaPhoto(media=banner.image, caption=banner.description) # Передаем баннер и описание
    categories = await orm_get_categories(session) # Получить категории
    kbds = get_user_catalog_btns(level=level, categories=categories) # Клавиатура на Lvl 1
    return image, kbds


def pages(paginator: Paginator): # Реализация Страниц и кнопок назад вперед
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"
    if paginator.has_next():
        btns["След. ▶"] = "next"
    return btns


async def products(session, level, category, page): # Lvl 2 и все что с ним должно выводиться 
    products = await orm_get_products(session, category_id=category) # Получить продукты
    paginator = Paginator(products, page=page) # Страница 1 
    product = paginator.get_page()[0] # Получаем список поэтому по индексу берем, первым - 0
    image = InputMediaPhoto(
        media=product.image,
        caption=f"<strong>{product.name}\
                </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}\n\
                <strong>Товар {paginator.page} из {paginator.pages}</strong>",
    )
    pagination_btns = pages(paginator) # Подтягиваем кнопки назад вперед
    kbds = get_products_btns(
        level=level,
        category=category,
        page=page,
        pagination_btns=pagination_btns,
        product_id=product.id,
    )
    return image, kbds


async def carts(session, level, menu_name, page, user_id, product_id): # Lvl 3 и все что с ним должно выводиться 
    if menu_name == "delete":
        await orm_delete_from_cart(session, user_id, product_id) # Удалить из корзины
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await orm_reduce_product_in_cart(session, user_id, product_id) # Уменьшить количество в корзине
        if page > 1 and not is_cart:
            page -= 1
    elif menu_name == "increment":
        await orm_add_to_cart(session, user_id, product_id) # Добавить в корзину
    carts = await orm_get_user_carts(session, user_id) # Получить все корзины
    if not carts:
        banner = await orm_get_banner(session, "cart")
        image = InputMediaPhoto(media=banner.image, caption=f"<strong>{banner.description}</strong>")
        kbds = get_user_cart(level=level, page=None, pagination_btns=None, product_id=None)
    else:
        paginator = Paginator(carts, page=page)
        cart = paginator.get_page()[0] # Получаем список поэтому по индексу берем, первым - 0
        cart_price = round(cart.quantity * cart.product.price, 2) # Общая цена по корзине
        total_price = round(sum(cart.quantity * cart.product.price for cart in carts), 2) # Общая цена по корзинам
        image = InputMediaPhoto(
            media=cart.product.image,
            caption=f"<strong>{cart.product.name}</strong>\n{cart.product.price}$ x {cart.quantity} = {cart_price}$\
                    \nТовар {paginator.page} из {paginator.pages} в корзине.\nОбщая стоимость товаров в корзине {total_price}",
        )
        pagination_btns = pages(paginator) # Подтягиваем кнопки назад вперед
        kbds = get_user_cart(level=level, page=page, pagination_btns=pagination_btns, product_id=cart.product.id)
    return image, kbds


async def get_menu_content( 
    session: AsyncSession,
    level: int,
    menu_name: str,
    category: int | None = None,
    page: int | None = None,
    product_id: int | None = None,
    user_id: int | None = None,
): # Принять от хендлера аргументы
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category, page)
    elif level == 3:
        return await carts(session, level, menu_name, page, user_id, product_id)