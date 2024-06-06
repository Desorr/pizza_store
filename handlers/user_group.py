from string import punctuation

from aiogram import F, Bot, types, Router
from aiogram.filters import Command
from filters.chat_types import ChatTypeFilter
from common.restricted_words import restricted_words

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup'])) # Сообщения которые работают в группе
user_group_router.edited_message.filter(ChatTypeFilter(['group', 'supergroup'])) # Измененные сообщения которые работают в группе


@user_group_router.message(Command("admin")) # Команда админ
async def get_admins(message: types.Message, bot: Bot):
    chat_id = message.chat.id # Получаем id чата
    admins_list = await bot.get_chat_administrators(chat_id) # Получаем id администраторов
    admins_list = [ 
        member.user.id for member in admins_list if member.status == "creator" or member.status == "administrator"
    ] # Получаем список id из креаторов и админов группы
    bot.my_admins_list = admins_list # Соединяем со списком
    if message.from_user.id in admins_list: # Удалить сообщение-проверка на админа в чате 
        await message.delete()    


def clean_text(text: str): # Проверка на скрытие/модернизацию запрещенных слов с помощью знаков препинаний
    return text.translate(str.maketrans('', '', punctuation))


@user_group_router.edited_message() # Измененные сообщения
@user_group_router.message() # Сообщения
async def cleaner(message: types.Message):
    if restricted_words.intersection(clean_text(message.text.lower()).split()): # Проверка
        await message.answer(f"{message.from_user.first_name}, соблюдайте порядок в чате!")
        await message.delete()
        # await message.chat.ban(message.from_user.id)