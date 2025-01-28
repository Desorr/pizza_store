# Telegram Pizza Bot

Этот проект представляет собой Telegram-бота для продажи пиццы с использованием **FastAPI** и **aiogram**. Бот позволяет пользователю оформить заказ, выбрать пиццу, оплатить её через платежный шлюз и получать подтверждение. Проект использует **PostgreSQL** для хранения данных и **Docker** для деплоя.

## Функциональность

- **Регистрация и авторизация пользователей**: Пользователи могут взаимодействовать с ботом через личные сообщения или групповые чаты.
- **Корзина покупок**: Пользователи могут добавлять пиццы в корзину и оформлять заказ.
- **Платежи через Redsys**: Поддержка оплаты через платежный шлюз Redsys.
- **Административная панель**: Администраторы могут управлять заказами и отслеживать статистику.
- **Вебхук**: Для обработки запросов используется вебхук.

## Установка

### Требования

1. Python 3.8+
2. Docker (для контейнеризации)
3. PostgreSQL (или используйте Docker для локальной базы данных)
4. FastAPI
5. Aiogram 3.0+

### Шаги для установки

1. **Клонируйте репозиторий:**

    ```bash
    git clone https://github.com/Desorr/pizza_store.git
    cd pizza_store
    ```

2. **Создайте файл `.env`:**

    В корневой директории проекта создайте файл `.env` и добавьте в него следующие строки:

    ```bash
    TOKEN=your-telegram-bot-token
    WEBHOOK_URL=your-webhook-url
    REDSYS_TEST_PROVIDER_TOKEN=your-redsys-provider-token
    DB_URL=postgresql://username:password@localhost:5432/db_name
    POSTGRES_USER=name
    POSTGRES_PASSWORD=password
    POSTGRES_DB=name
    ```

3. **Установите зависимости:**

    Используйте `pip` для установки зависимостей:

    ```bash
    pip install -r requirements.txt
    ```

4. **Запуск проекта с использованием Docker:**

    Для контейнеризации проекта используйте Docker. В корневой директории проекта выполните команду:

    ```bash
    docker-compose up --build
    ```

    Это создаст и запустит контейнеры для приложения и базы данных PostgreSQL.

### Запуск без Docker

Если вы хотите запустить проект без Docker, выполните следующие шаги:

1. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

2. Запустите приложение:

    ```bash
    uvicorn main:app --reload
    ```

## Структура проекта


telegram-pizza-bot/             
├── common/  
│ ├── restricted_words.py # Запрещенные слова  
│ └── texts_for_db.py # Тексты для бота    
├── filters/   
│ └── chat_types.py # Фильтрует события и права         
├── handlers/   
│ ├── user_private.py # Обработчики для личных сообщений пользователей  
│ ├── user_group.py # Обработчики для групповых чатов  
│ ├── menu_processing.py # Обработчики меню в зависимости от lvl                                 
│ ├── admin_private.py # Обработчики для администратора               
│ └── payment_redsys.py # Обработчики для оплаты через Redsys    
├── middlewares/    
│ └── db.py # Middleware для работы с базой данных   
├── kbds/   
│ ├── inline.py # Инлайн клавиатура   
│ └── reply.py # Реплай клавиатура  
├── database/   
│ ├── engine.py # Настройка подключения к базе данных   
│ ├── models.py # Модели для SQLAlchemy                                                   
│ ├── schemas_models.py # Валидация                                                          
│ └── orm_query.py # Операции с базой данных через ORM  
├── utils/   
│ ├── banner_change.py # Преобразование данных  
│ └── paginator.py # Пагинация  
├── .gitignore # Игноры                                                      
├── .env # Файл с переменными окружения     
├── app.py # Основной файл для запуска FastAPI                                 
├── docker-compose.yml # Конфигурация Docker  
├── Dockerfile # Docker                                                                         
├── Dockerfile # Docker                                                                         
├── wait-for-it.sh # Ожидания подключений    
└── README.md # Описание проекта 


## Настройка вебхука

1. Для установки вебхука на сервере необходимо указать переменную `WEBHOOK_URL` в файле `.env`.
2. После запуска приложения, бот автоматически установит вебхук для обработки входящих обновлений от Telegram.

## Платежи через Redsys

Для интеграции с платежной системой Redsys необходимо получить токен от провайдера и указать его в файле `.env` в переменной `REDSYS_TEST_PROVIDER_TOKEN`.

## Лицензия
Этот проект распространяется под лицензией MIT. Подробности можно найти в файле LICENSE