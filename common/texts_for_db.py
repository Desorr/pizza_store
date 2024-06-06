from aiogram.utils.formatting import Bold, as_list, as_marked_section


categories = ['Еда', 'Напитки']

description_for_info_pages = {
    "main": "Добро пожаловать!",
    "about": "Пиццерия Такая-то.\nРежим работы - круглосуточно.",
    "payment": as_marked_section( # Обернуть секцию
        Bold("Варианты оплаты:"), # Жирный текст
        "Картой в боте",
        "При получении карта/кеш",
        "В заведении",
        marker="✅ ",
    ).as_html(),
    "shipping": as_list(
        as_marked_section( # Обернуть секцию
            Bold("Варианты доставки/заказа:"), # Жирный текст
            "Курьер",
            "Самовынос (сейчас прибегу заберу)",
            "Покушаю у Вас (сейчас прибегу)",
            marker="✅ ",
        ),
        as_marked_section(Bold("Нельзя:"), "Почта", "Голуби", marker="❌ "), # Обернуть секцию
        sep="\n----------------------\n", # Разделитель
    ).as_html(),
    'catalog': 'Категории:',
    'cart': 'В корзине ничего нет!'
}