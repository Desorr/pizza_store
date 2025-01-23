from pydantic import BaseModel, Field
from typing import Optional


# Баннеры 
class BannerBase(BaseModel):
    image: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = Field(None)

class BannerCreate(BannerBase):
    name: str = Field(..., max_length=50)

class BannerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    image: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = Field(None)

class BannerSchema(BannerBase):
    id: int
    name: str

    class Config:
        from_attributes = True  


# Категории
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=150)

class CategoryCreate(CategoryBase):
    pass

class CategorySchema(CategoryBase):
    id: int

    class Config:
        from_attributes = True 


# Продукты 
class ProductBase(BaseModel):
    name: str = Field(..., max_length=150)
    description: str
    price: float = Field(..., gt=0)  # Цена должна быть больше 0
    image: str = Field(..., max_length=150)
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    description: Optional[str]
    price: Optional[float] = Field(None, gt=0)
    image: Optional[str] = Field(None, max_length=150)
    category_id: Optional[int] 

class ProductSchema(ProductBase):
    id: int

    class Config:
        from_attributes = True


# Пользователи
class UserBase(BaseModel):
    user_id: int
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = Field(None, max_length=13)

class UserCreate(UserBase):
    pass

class UserSchema(UserBase):
    id: int

    class Config:
        from_attributes = True