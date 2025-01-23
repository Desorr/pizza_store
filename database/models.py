from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseTimestampMixin:
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Base(BaseTimestampMixin, DeclarativeBase):
    pass


class Banner(Base):
    __tablename__ = 'banner' 
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) 
    name: Mapped[str] = mapped_column(String(15), unique=True) 
    image: Mapped[str] = mapped_column(String(150), nullable=True) 
    description: Mapped[str] = mapped_column(Text, nullable=True) 


class Category(Base):
    __tablename__ = 'category' 
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) 
    name: Mapped[str] = mapped_column(String(150), nullable=False) 


class Product(Base):
    __tablename__ = 'product' 
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) 
    name: Mapped[str] = mapped_column(String(150), nullable=False) 
    description: Mapped[str] = mapped_column(Text) 
    price: Mapped[float] = mapped_column(Numeric(5,2), nullable=False) 
    image: Mapped[str] = mapped_column(String(150))  
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'), nullable=False)
    category: Mapped['Category'] = relationship(backref='product') # Обратная связь, чтобы могли делать выборку из БД связанных моделей(категория-продукт)


class User(Base):
    __tablename__ = 'user' 
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True) 
    first_name: Mapped[str] = mapped_column(String(150), nullable=True) 
    last_name: Mapped[str]  = mapped_column(String(150), nullable=True)
    phone: Mapped[str]  = mapped_column(String(13), nullable=True) 


class Cart(Base):
    __tablename__ = 'cart' 
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) 
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id'), nullable=False) 
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id'), nullable=False) 
    quantity: Mapped[int] 
    user: Mapped['User'] = relationship(backref='cart') # Обратная связь, чтобы могли делать выборку из БД связанных моделей(пользователь-корзина)
    product: Mapped['Product'] = relationship(backref='cart') # Обратная связь, чтобы могли делать выборку из БД связанных моделей(продукт-корзина)