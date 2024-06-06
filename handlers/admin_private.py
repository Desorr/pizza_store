from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import (
    orm_change_banner_image,
    orm_get_categories,
    orm_add_product,
    orm_delete_product,
    orm_get_info_pages,
    orm_get_product,
    orm_get_products,
    orm_update_product,
)
from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


ADMIN_KB = get_keyboard(
    "Добавить товар",
    "Ассортимент",
    "Добавить/Изменить баннер",
    placeholder="Выберите действие",
    sizes=(2,),
)


@admin_router.message(Command("admin"))
async def add_product(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)    


@admin_router.message(F.text == 'Ассортимент')
async def admin_features(message: types.Message, session: AsyncSession):
    categories = await orm_get_categories(session) # Получить категории
    btns = {category.name : f'category_{category.id}' for category in categories} # Названия категорий
    await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))


@admin_router.callback_query(F.data.startswith('category_'))
async def starring_at_product(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split('_')[-1]
    for product in await orm_get_products(session, int(category_id)): # Получить продукты
        await callback.message.answer_photo( # Информация о продукте
            product.image,
            caption=f"<strong>{product.name}\
                    </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}",
            reply_markup=get_callback_btns( # Действия с продуктом
                btns={
                    "Удалить": f"delete_{product.id}",
                    "Изменить": f"change_{product.id}",
                },
                sizes=(2,)
            ),
        )
    await callback.answer()
    await callback.message.answer("ОК, вот список товаров ⏫")


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession): # Удаление из БД при нажатии на инлайн кнопку
    product_id = callback.data.split("_")[-1]  # Получить id разделить по _ в фразе "delete_{product.id}"
    await orm_delete_product(session, int(product_id)) # Удалить определенный продукт
    await callback.answer("Товар удален") # Для бота, чтобы после нажатия не висели часики 
    await callback.message.answer("Товар удален!") # Сообщение в чат


################# Микро FSM для загрузки/изменения баннеров ############################
    
class AddBanner(StatesGroup): # Добавить баннер
    image = State() # Состояние


# Отправляем перечень информационных страниц бота и становимся в состояние отправки photo
@admin_router.message(StateFilter(None), F.text == 'Добавить/Изменить баннер') # Изначально State - None
async def add_image2(message: types.Message, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)] # Получить названия страниц
    await message.answer(f"Отправьте фото баннера.\nВ описании укажите для какой страницы:\
                         \n{', '.join(pages_names)}")
    await state.set_state(AddBanner.image) # Установить состояние на ввода баннера


# Добавляем/изменяем изображение в таблице (там уже есть записанные страницы по именам: main, catalog, cart(для пустой корзины), about, payment, shipping
@admin_router.message(AddBanner.image, F.photo) # Ввести новый баннер
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id # id баннера
    for_page = message.caption.strip() # Чтобы убрать если вдруг будет пробел при вводе названия страницы
    pages_names = [page.name for page in await orm_get_info_pages(session)] # Названия страниц
    if for_page not in pages_names:
        await message.answer(f"Введите нормальное название страницы, например:\
                         \n{', '.join(pages_names)}")
        return
    await orm_change_banner_image(session, for_page, image_id,) # Изменить баннер для определенной страницы
    await message.answer("Баннер добавлен/изменен.")
    await state.clear() # Очистить состояние пользователя и удалить полученные данные из FSM

# Хендлер для отлова некоррекного ввода
@admin_router.message(AddBanner.image)
async def add_banner2(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото баннера или отмена")


######################### FSM для дабавления/изменения товаров админом ###################
    
class AddProduct(StatesGroup): # Добавить продукт
    name = State() # Состояние
    description = State() # Состояние
    category = State() # Состояние
    price = State() # Состояние 
    image = State() # Состояние

    product_for_change = None

    texts = {
        "AddProduct:name": "Введите название заново:",
        "AddProduct:description": "Введите описание заново:",
        "AddProduct:category": "Выберите категорию  заново ⬆️",
        "AddProduct:price": "Введите стоимость заново:",
        "AddProduct:image": "Этот стейт последний, поэтому...",
    }    


# Становимся в состояние ожидания ввода name
@admin_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_product_callback(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession): # Изменение продукта в БД при нажатии на инлайн кнопку
    product_id = callback.data.split("_")[-1] # Получить id разделить по _ в фразе "change_{product.id}"
    product_for_change = await orm_get_product(session, int(product_id)) # Получить определенный продукт
    AddProduct.product_for_change = product_for_change
    await callback.answer() # Для бота, чтобы после нажатия не висели часики 
    await callback.message.answer("Введите название товара", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)  # Установить состояние на ввод имени


# Становимся в состояние ожидания ввода name
@admin_router.message(StateFilter(None), F.text == "Добавить товар") # Изначально State - None
async def add_product(message: types.Message, state: FSMContext):
    await message.answer("Введите название товара", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.name) # Установить состояние на ввод имени


# Хендлер отмены и сброса состояния должен быть всегда именно здесь,после того как только встали в состояние номер 1
@admin_router.message(StateFilter('*'), Command("отмена")) # Фильтр - любое состояние пользователя, команда-отмена
@admin_router.message(StateFilter('*'), F.text.casefold() == "отмена") # Фильтр - любое состояние пользователя, текст-отмена
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state() # Текущее состояние
    if current_state is None:
        return
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    await state.clear() # Очистить состояние пользователя и удалить полученные данные из FSM
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)


# Вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter('*'), Command("назад")) # Фильтр - любое состояние пользователя, команда-назад
@admin_router.message(StateFilter('*'), F.text.casefold() == "назад") # Фильтр - любое состояние пользователя, текст-назад
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state() # Текущее состояние
    if current_state == AddProduct.name:
        await message.answer('Предыдущего шага нет, или введите название товара или напишите "отмена"')
        return
    previous = None # Предыдущее состояние
    for step in AddProduct.__all_states__: # Проходим по всем состояниям
        if step.state == current_state:
            await state.set_state(previous) # Возвращение к предыдущему состоянию
            await message.answer(f"Ок, вы вернулись к прошлому шагу \n {AddProduct.texts[previous.state]}")
            return
        previous = step

# Ловим данные для состояния name и потом меняем состояние на description
@admin_router.message(AddProduct.name, F.text) # Ввести новое название
async def add_name(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(name=AddProduct.product_for_change.name) # Оставить название которое было
    else:
        if len(message.text) >= 100: # Можно добавить любую проверку
            await message.answer("Название товара не должно превышать 100 символов. \n Введите заново")
            return
    await state.update_data(name=message.text) # Записываем данные от пользователя в имя
    await message.answer("Введите описание товара")
    await state.set_state(AddProduct.description) # Установить состояние на ввод описания

# Хендлер для отлова некорректного ввода для состояния name
@admin_router.message(AddProduct.name)
async def add_name2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите текст названия товара")


# Ловим данные для состояние description и потом меняем состояние на category
@admin_router.message(AddProduct.description, F.text) # Ввести новое описание
async def add_description(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(description=AddProduct.product_for_change.description) # Оставить описание которое было
    else:
        if 4 >= len(message.text):
            await message.answer(
                "Слишком короткое описание. \n Введите заново"
            )
            return
        await state.update_data(description=message.text) # Изменить описание
    categories = await orm_get_categories(session) # Получить категории
    btns = {category.name : str(category.id) for category in categories} # Категория 1,2,.. 
    await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddProduct.category) # Установить состояние на ввод категории

# Хендлер для отлова некорректного ввода для состояния description
@admin_router.message(AddProduct.description)
async def add_description2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите текст описания товара")


# Ловим callback выбора категории
@admin_router.callback_query(AddProduct.category) # Выбрать категорию
async def category_choice(callback: types.CallbackQuery, state: FSMContext , session: AsyncSession):
    if int(callback.data) in [category.id for category in await orm_get_categories(session)]:
        await callback.answer()
        await state.update_data(category=callback.data) # Добавляется в БД выбранная категория
        await callback.message.answer('Теперь введите цену товара.')
        await state.set_state(AddProduct.price) # Установить состояние на ввод категории
    else:
        await callback.message.answer('Выберите катеорию из кнопок.')
        await callback.answer()

# Хендлер для отлова любых некорректных действий, кроме нажатия на кнопку выбора категории
@admin_router.message(AddProduct.category)
async def category_choice2(message: types.Message, state: FSMContext):
    await message.answer("'Выберите катеорию из кнопок.'") 


# Ловим данные для состояние price и потом меняем состояние на image
@admin_router.message(AddProduct.price, F.text) # Ввести новую цену
async def add_price(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(price=AddProduct.product_for_change.price) # Оставить цену которая была
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer("Введите корректное значение цены")
            return
        await state.update_data(price=message.text) # Записываем данные от пользователя в прайс
    await message.answer("Загрузите изображение товара")
    await state.set_state(AddProduct.image) # Установить состояние на ввод изображения

# Хендлер для отлова некорректного ввода для состояния price
@admin_router.message(AddProduct.price)
async def add_price2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите стоимость товара")


# Ловим данные для состояние image и потом выходим из состояний
@admin_router.message(AddProduct.image, or_f(F.photo, F.text == ".")) # Добавить новое изображение или оставить то, что было
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == ".":
        await state.update_data(image=AddProduct.product_for_change.image) # Оставить изображение которое было    
    else:
        await state.update_data(image=message.photo[-1].file_id) # Записываем данные от пользователя в изображение
    data = await state.get_data() # Сохранить словарь с добавленными значениями
    try:   
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data) # Изменить объект в БД
        else: 
            await orm_add_product(session, data) # Добавить объект в БД
        await message.answer("Товар добавлен/изменен", reply_markup=ADMIN_KB)
        await state.clear() # Очистить состояние пользователя и удалить полученные данные из FSM
    except Exception as e:
        await message.answer(
            f"Ошибка: \n{str(e)}\nОбратись к программеру, он опять денег хочет",
            reply_markup=ADMIN_KB,
        )
        await state.clear() # Очистить состояние пользователя и удалить полученные данные из FSM
    AddProduct.product_for_change = None # После изменения снова вернуть в None

# Хендлер для отлова некорректного ввода для состояния image
@admin_router.message(AddProduct.image)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото пищи")
    