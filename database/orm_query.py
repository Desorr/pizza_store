from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from database.models import Banner, Cart, Category, Product, User


############### Работа с баннерами (информационными страницами) ###############

async def orm_add_banner_description(session: AsyncSession, data: dict): # Добавить описание для баннеров
    query = select(Banner) # Выбор всех записей из БД
    result = await session.execute(query) # Выполнить запрос
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()]) # Добавить
    await session.commit() # Закрепить данные в БД


async def orm_change_banner_image(session: AsyncSession, name: str, image: str): # Изменить баннер
    query = update(Banner).where(Banner.name == name).values(image=image) # Добавить новое фото для баннера
    await session.execute(query) # Выполнить запрос
    await session.commit() # Закрепить данные в БД


async def orm_get_banner(session: AsyncSession, page: str): # Получить баннер
    query = select(Banner).where(Banner.name == page) # Выбрать баннер, который подходит к определенной странице
    result = await session.execute(query) # Выполнить запрос
    return result.scalar() # Возвращаем в хэндлер


async def orm_get_info_pages(session: AsyncSession): # Получить страницу информации
    query = select(Banner) # Выбор всех записей из БД
    result = await session.execute(query) # Выполнить запрос
    return result.scalars().all() # Возвращаем в хэндлер всё


############################ Категории ######################################

async def orm_get_categories(session: AsyncSession): # Получить категории
    query = select(Category) # Выбор всех записей из БД
    result = await session.execute(query) # Выполнить запрос
    return result.scalars().all() # Возвращаем в хэндлер всё

async def orm_create_categories(session: AsyncSession, categories: list): # Создать категорию
    query = select(Category) # Выбор всех записей из БД
    result = await session.execute(query) # Выполнить запрос
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories]) # Добавить
    await session.commit() # Закрепить данные в БД

############ Админка: добавить/изменить/удалить товар ########################

async def orm_add_product(session: AsyncSession, data: dict): # Добавляем продукт
    obj = Product(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data["category"]), # Присваивается id определенной категории
    )
    session.add(obj) # Добавить объект в БД
    await session.commit() # Закрепить данные в БД


async def orm_get_products(session: AsyncSession, category_id): # Получить продукты
    query = select(Product).where(Product.category_id == int(category_id)) # Выбор всех записей из БД
    result = await session.execute(query) # Выполнить запрос
    return result.scalars().all() # Возвращаем в хэндлер всё


async def orm_get_product(session: AsyncSession, product_id: int): # Получить определенный продукт
    query = select(Product).where(Product.id == product_id) # Выбор определенной записи из БД
    result = await session.execute(query) # Выполнить запрос
    return result.scalar() # Возвращаем в хэндлер


async def orm_update_product(session: AsyncSession, product_id: int, data): # Изменить определенный продукт
    query = (
        update(Product).where(Product.id == product_id).values( # Вносим новые данные
            name=data["name"],
            description=data["description"],
            price=float(data["price"]),
            image=data["image"],
            category_id=int(data["category"]),
        )
    )
    await session.execute(query) # Выполнить запрос
    await session.commit() # Закрепить данные в БД


async def orm_delete_product(session: AsyncSession, product_id: int): # Удалить определенный продукт
    query = delete(Product).where(Product.id == product_id) # Выбор определенной записи из БД
    await session.execute(query) # Выполнить запрос
    await session.commit() # Закрепить данные в БД

##################### Добавляем юзера в БД #####################################

async def orm_add_user( session: AsyncSession, user_id: int, first_name: str | None = None, last_name: str | None = None, phone: str | None = None): # Добавить пользователя
    query = select(User).where(User.user_id == user_id) # Выбор определенного пользователя
    result = await session.execute(query) # Выполнить запрос
    if result.first() is None:
        session.add(User(user_id=user_id, first_name=first_name, last_name=last_name, phone=phone)) # Добавить
        await session.commit() # Закрепить данные в БД


######################## Работа с корзинами #######################################

async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int): # Добавить в корзину
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id).options(joinedload(Cart.product)) # Выбрать определенную корзину
    cart = await session.execute(query) # Выполнить запрос
    cart = cart.scalar() # Возвращаем в хэндлер
    if cart:
        cart.quantity += 1 # Увеличиваем количество
        await session.commit() # Закрепить данные в БД
        return cart 
    else:
        session.add(Cart(user_id=user_id, product_id=product_id, quantity=1)) # Добавить
        await session.commit() # Закрепить данные в БД



async def orm_get_user_carts(session: AsyncSession, user_id): # Получить корзины пользователя
    query = select(Cart).filter(Cart.user_id == user_id).options(joinedload(Cart.product)) # Выбрать корзины пользователя
    result = await session.execute(query) # Выполнить запрос
    return result.scalars().all() # Возвращаем в хэндлер всё


async def orm_delete_from_cart(session: AsyncSession, user_id: int, product_id: int): # Удалить из корзины
    query = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id) # Удалить определенную корзину пользователя
    await session.execute(query) # Выполнить запрос
    await session.commit() # Закрепить данные в БД


async def orm_reduce_product_in_cart(session: AsyncSession, user_id: int, product_id: int): # Уменьшить количество продукта в корзине
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id) # Выбрать корзину
    cart = await session.execute(query) # Выполнить запрос
    cart = cart.scalar() # Возвращаем в хэндлер

    if not cart: 
        return
    if cart.quantity > 1:
        cart.quantity -= 1 # Уменьшаем количество
        await session.commit() # Закрепить данные в БД
        return True
    else:
        await orm_delete_from_cart(session, user_id, product_id) # Удалить из корзины
        await session.commit() # Закрепить данные в БД
        return False
