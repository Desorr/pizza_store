from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from database.models import Banner, Cart, Category, Product, User
from database.schemas_models import ProductCreate, ProductUpdate, UserCreate, BannerUpdate
from pydantic import ValidationError


############### Работа с баннерами (информационными страницами) ###############

# Добавить описание для баннеров
async def orm_add_banner_description(session: AsyncSession, data: dict): 
    query = select(Banner) 
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()]) 
    await session.commit() 

# Изменить баннер
async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    banner_data = BannerUpdate(image=image) 
    query = update(Banner).where(Banner.name == name).values(image=banner_data.image)
    await session.execute(query) 
    await session.commit() 

# Получить баннер
async def orm_get_banner(session: AsyncSession, page: str): 
    query = select(Banner).where(Banner.name == page) 
    result = await session.execute(query) 
    return result.scalar() 

# Получить страницу информации
async def orm_get_info_pages(session: AsyncSession): 
    query = select(Banner) 
    result = await session.execute(query) 
    return result.scalars().all() 

############################ Категории ######################################

# Получить категории
async def orm_get_categories(session: AsyncSession): 
    query = select(Category) 
    result = await session.execute(query) 
    return result.scalars().all() 

# Создать категорию
async def orm_create_categories(session: AsyncSession, categories: list): 
    query = select(Category) 
    result = await session.execute(query) 
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories]) 
    await session.commit() 

############ Админка: добавить/изменить/удалить товар ########################

# Добавляем продукт
async def orm_add_product(session: AsyncSession, data: dict): 
    try:
        product_data = ProductCreate(**data)
    except ValidationError as e:
        raise Exception(f"Ошибка валидации данных продукта: {e}")
    
    obj = Product(
        name=product_data.name, 
        description=product_data.description,
        price=product_data.price,
        image=product_data.image,
        category_id=product_data.category_id,
    )
    
    session.add(obj) 
    await session.commit() 

# Получить продукты
async def orm_get_products(session: AsyncSession, category_id): 
    query = select(Product).where(Product.category_id == int(category_id)) 
    result = await session.execute(query) 
    return result.scalars().all() 

# Получить определенный продукт
async def orm_get_product(session: AsyncSession, product_id: int): 
    query = select(Product).where(Product.id == product_id) 
    result = await session.execute(query) 
    return result.scalar() 

# Изменить определенный продукт
async def orm_update_product(session: AsyncSession, product_id: int, data: dict):
    try:
        product_data = ProductUpdate(**data)
    except ValidationError as e:
        raise Exception(f"Ошибка валидации данных продукта: {e}")

    query = (update(Product).where(Product.id == product_id) .values(
            name=product_data.name,
            description=product_data.description,
            price=float(product_data.price),
            image=product_data.image,
            category_id=int(product_data.category_id),
        )
    )
    await session.execute(query) 
    await session.commit() 

# Удалить определенный продукт
async def orm_delete_product(session: AsyncSession, product_id: int): 
    query = delete(Product).where(Product.id == product_id) 
    await session.execute(query) 
    await session.commit() 

##################### Добавляем юзера в БД #####################################

# Добавить пользователя
async def orm_add_user(session: AsyncSession, user_id: int, first_name: str | None = None, last_name: str | None = None, phone: str | None = None): 
    try:
        user_data = UserCreate(user_id=user_id, first_name=first_name, last_name=last_name, phone=phone)
    except ValidationError as e:
        raise ValueError(f"Ошибка валидации данных пользователя: {e}")
    
    query = select(User).where(User.user_id == user_id) 
    result = await session.execute(query) 
    if result.first() is None:
        session.add(User(**user_data.model_dump()))
        await session.commit()

######################## Работа с корзинами #######################################

# Добавить в корзину
async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int): 
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id).options(joinedload(Cart.product))
    cart = await session.execute(query) 
    cart = cart.scalar() 
    if cart:
        cart.quantity += 1 
        await session.commit() 
        return cart 
    else:
        session.add(Cart(user_id=user_id, product_id=product_id, quantity=1)) 
        await session.commit() 

# Получить корзины пользователя
async def orm_get_user_carts(session: AsyncSession, user_id): 
    query = select(Cart).filter(Cart.user_id == user_id).options(joinedload(Cart.product)) 
    result = await session.execute(query) 
    return result.scalars().all() 

# Удалить из корзины
async def orm_delete_from_cart(session: AsyncSession, user_id: int, product_id: int): 
    query = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id) 
    await session.execute(query) 
    await session.commit() 

# Уменьшить количество продукта в корзине
async def orm_reduce_product_in_cart(session: AsyncSession, user_id: int, product_id: int): 
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id) 
    cart = await session.execute(query) 
    cart = cart.scalar()

    if not cart: 
        return
    if cart.quantity > 1:
        cart.quantity -= 1 
        await session.commit() 
        return True
    else:
        await orm_delete_from_cart(session, user_id, product_id) 
        await session.commit() 
        return False
