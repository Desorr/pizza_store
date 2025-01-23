from pydantic import ValidationError
from database.schemas_models import BannerCreate


# Преобразование данных для модели BannerCreate
def prepare_banner_data(description_for_info_pages):
    banner_data_list = []
    for key, value in description_for_info_pages.items():
        banner_data = {
            "name": key, 
            "description": value,  
            "image": None  
        }
        try:
            banner_data_list.append(BannerCreate(**banner_data))
        except ValidationError as e:
            print(f"Ошибка валидации данных баннера для ключа {key}: {e}")
    return banner_data_list
