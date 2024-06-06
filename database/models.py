from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase): # Класс от которого идут наследования
    # Mapped[] - Проставить аннотацию типа, далее добавить параметры 
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Banner(Base):
    __tablename__ = 'banner' # Название таблицы
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # id
    name: Mapped[str] = mapped_column(String(15), unique=True) # Название
    image: Mapped[str] = mapped_column(String(150), nullable=True) # Картинка
    description: Mapped[str] = mapped_column(Text, nullable=True) # Описание


class Category(Base):
    __tablename__ = 'category' # Название таблицы
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # id
    name: Mapped[str] = mapped_column(String(150), nullable=False) # Название


class Product(Base):
    __tablename__ = 'product' # Название таблицы
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # id
    name: Mapped[str] = mapped_column(String(150), nullable=False) # Название
    description: Mapped[str] = mapped_column(Text) # Описание
    price: Mapped[float] = mapped_column(Numeric(5,2), nullable=False) # Цена
    image: Mapped[str] = mapped_column(String(150))  # Картинка
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'), nullable=False) # Ссылаемся на id в таблице категории
    category: Mapped['Category'] = relationship(backref='product') # Обратная связь, чтобы могли делать выборку из БД связанных моделей(категория-продукт)


class User(Base):
    __tablename__ = 'user' # Название таблицы
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # id
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True) # id в тг
    first_name: Mapped[str] = mapped_column(String(150), nullable=True) # Имя
    last_name: Mapped[str]  = mapped_column(String(150), nullable=True) # Фамилия
    phone: Mapped[str]  = mapped_column(String(13), nullable=True) # Телефон


class Cart(Base):
    __tablename__ = 'cart' # Название таблицы
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # id
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id'), nullable=False) # Ссылаемся на id в тг в таблице пользователь
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id'), nullable=False) # Ссылаемся на id в таблице продукты
    quantity: Mapped[int] # Количество
    user: Mapped['User'] = relationship(backref='cart') # Обратная связь, чтобы могли делать выборку из БД связанных моделей(пользователь-корзина)
    product: Mapped['Product'] = relationship(backref='cart') # Обратная связь, чтобы могли делать выборку из БД связанных моделей(продукт-корзина)