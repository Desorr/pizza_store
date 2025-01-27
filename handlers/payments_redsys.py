import hashlib
import base64
import hmac
from urllib.parse import urlencode

from aiogram import Router, types
from aiogram.types import CallbackQuery

pay_redsys_router = Router()

# Конфигурация Redsys
REDSYS_SECRET_KEY = "2051251535:TEST:OTk5MDA4ODgxLTAwNQ"  # Тестовый ключ
REDSYS_URL = "https://sis-t.redsys.es:25443/sis/realizarPago"
MERCHANT_CODE = "999008881"  # Тестовый код продавца
TERMINAL = "1"              # Тестовый терминал
CURRENCY = "978"            # Евро (ISO 4217)

# Функция для генерации подписи
def generate_signature(order_id: str, amount: str) -> str:
    payload = f"{amount}{order_id}{MERCHANT_CODE}{CURRENCY}{TERMINAL}0https://yourdomain.com/notify"
    key = base64.b64decode(REDSYS_SECRET_KEY)
    mac = hmac.new(key, payload.encode('utf-8'), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode('utf-8')

# Функция для создания ссылки на оплату
def create_payment_url(order_id: str, amount: str) -> str:
    signature = generate_signature(order_id, amount)
    params = {
        "Ds_Merchant_Amount": amount,
        "Ds_Merchant_Order": order_id,
        "Ds_Merchant_MerchantCode": MERCHANT_CODE,
        "Ds_Merchant_Currency": CURRENCY,
        "Ds_Merchant_Terminal": TERMINAL,
        "Ds_Merchant_TransactionType": "0",
        "Ds_Merchant_MerchantURL": "https://yourdomain.com/notify",
        "Ds_Merchant_UrlOK": "https://yourdomain.com/success",
        "Ds_Merchant_UrlKO": "https://yourdomain.com/failure",
        "Ds_Merchant_Signature": signature
    }
    return f"{REDSYS_URL}?{urlencode(params)}"

# Обработчик нажатия на кнопку "Заказать"
@pay_redsys_router.callback_query(lambda c: c.data == "order_payment")
async def handle_order_payment(query: CallbackQuery):
    user_id = query.from_user.id
    order_id = f"{user_id}0001"  # Пример ID заказа
    amount = "100"  # Сумма в центах (например, 1 евро = 100)

    # Генерация ссылки для оплаты
    payment_url = create_payment_url(order_id, amount)

    # Отправляем ссылку пользователю
    await query.message.edit_text(
        f"Для оплаты перейдите по ссылке: [Оплатить]({payment_url})",
        parse_mode="Markdown"
    )
