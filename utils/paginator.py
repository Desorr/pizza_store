import math


# Пагинатор
class Paginator:
    def __init__(self, array: list | tuple, page: int=1, per_page: int=1):
        self.array = array
        self.per_page = per_page
        self.page = page
        self.len = len(self.array)
        self.pages = math.ceil(self.len / self.per_page) # math.ceil - округление в большую сторону до целого числа

    def __get_slice(self):
        start = (self.page - 1) * self.per_page
        stop = start + self.per_page
        return self.array[start:stop]

    def get_page(self): # Получить страницу
        page_items = self.__get_slice()
        return page_items

    def has_next(self): # Есть ли следующая страница
        if self.page < self.pages:
            return self.page + 1
        return False

    def has_previous(self): # Есть ли предыдущая страница
        if self.page > 1:
            return self.page - 1
        return False

    def get_next(self): # Перейти на следующую страницу
        if self.page < self.pages:
            self.page += 1
            return self.get_page()
        raise IndexError(f'Next page does not exist. Use has_next() to check before.')

    def get_previous(self): # Перейти на предыдущую страницу
        if self.page > 1:
            self.page -= 1
            return self.__get_slice()
        raise IndexError(f'Previous page does not exist. Use has_previous() to check before.')
    