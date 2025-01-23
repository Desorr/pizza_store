from aiogram.filters import Filter
from aiogram import Bot, types


# Фильтрует события в зависимости от того, в каком чате находимся(БОТ или Группа)
class ChatTypeFilter(Filter): 
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types
    async def __call__(self, message: types.Message) -> bool: # Переброс сообщения в нужный чат
        return message.chat.type in self.chat_types

# Фильтруем на права Администратора
class IsAdmin(Filter): 
    def __init__(self) -> None:
        pass
    async def __call__(self, message: types.Message, bot: Bot) -> bool: # Проверка сообщения по id от админа
        return message.from_user.id in bot.my_admins_list
  