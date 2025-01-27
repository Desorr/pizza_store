from aiogram.types import InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
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
from kbds.inline import MenuCallBack, get_callback_btns, get_products_btns, get_user_cart, get_user_catalog_btns, get_user_main_btns
from utils.paginator import Paginator


# Главное меню
async def main_menu(session, level, menu_name): # Lvl 0 и все что с ним должно выводиться 
    banner = await orm_get_banner(session, menu_name) 
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbds = get_user_main_btns(level=level)
    return image, kbds

# Каталог
async def catalog(session, level, menu_name): # Lvl 1
    banner = await orm_get_banner(session, menu_name) 
    image = InputMediaPhoto(media=banner.image, caption=banner.description) 
    categories = await orm_get_categories(session)
    kbds = get_user_catalog_btns(level=level, categories=categories) 
    return image, kbds

# Пагинация
def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"
    if paginator.has_next():
        btns["След. ▶"] = "next"
    return btns

# Товары
async def products(session, level, category, page): # Lvl 2 
    products = await orm_get_products(session, category_id=category) 
    paginator = Paginator(products, page=page) 
    product = paginator.get_page()[0]
    image = InputMediaPhoto(
        media=product.image,
        caption=f"<strong>{product.name}\
                </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}\n\
                <strong>Товар {paginator.page} из {paginator.pages}</strong>",
    )
    pagination_btns = pages(paginator)
    kbds = get_products_btns(
        level=level,
        category=category,
        page=page,
        pagination_btns=pagination_btns,
        product_id=product.id,
    )
    return image, kbds

# Корзина
async def carts(session, level, menu_name, page, user_id, product_id): # Lvl 3 
    if menu_name == "delete":
        await orm_delete_from_cart(session, user_id, product_id) 
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await orm_reduce_product_in_cart(session, user_id, product_id) 
        if page > 1 and not is_cart:
            page -= 1
    elif menu_name == "increment":
        await orm_add_to_cart(session, user_id, product_id) 
    carts = await orm_get_user_carts(session, user_id) 
    if not carts:
        banner = await orm_get_banner(session, "cart")
        image = InputMediaPhoto(media=banner.image, caption=f"<strong>{banner.description}</strong>")
        kbds = get_user_cart(level=level, page=None, pagination_btns=None, product_id=None)
    else:
        paginator = Paginator(carts, page=page)
        cart = paginator.get_page()[0]
        cart_price = round(cart.quantity * cart.product.price, 2) 
        total_price = round(sum(cart.quantity * cart.product.price for cart in carts), 2) 
        image = InputMediaPhoto(
            media=cart.product.image,
            caption=f"<strong>{cart.product.name}</strong>\n{cart.product.price}$ x {cart.quantity} = {cart_price}$\
                    \nТовар {paginator.page} из {paginator.pages} в корзине.\nОбщая стоимость товаров в корзине {total_price}",
        )
        pagination_btns = pages(paginator) 
        kbds = get_user_cart(level=level, page=page, pagination_btns=pagination_btns, product_id=cart.product.id)
    return image, kbds

# Оплата
async def payment(session, level, user_id):  # Lvl 4
    banner = await orm_get_banner(session, "payments")
    payment_url = f"https://example.com/payment?user_id={user_id}"
    
    # Создание изображения с описанием
    image = InputMediaPhoto(
        media=banner.image,
        caption=f"<strong>{banner.description}</strong>\n\nДля оплаты нажмите на кнопку ниже."
    )
    
    # Создание клавиатуры вручную
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
            text="Оплатить 💳",
            url=payment_url  # URL-кнопка
        ))
    
    return image, keyboard.as_markup()


# Получить меню в зависимости от аргументов
async def get_menu_content( 
    session: AsyncSession,
    level: int,
    menu_name: str,
    category: int | None = None,
    page: int | None = None,
    product_id: int | None = None,
    user_id: int | None = None,
):
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category, page)
    elif level == 3:
        return await carts(session, level, menu_name, page, user_id, product_id)
    elif level == 4:
        return await payment(session, level, user_id)