import os
from aiogram import Router, types
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_get_user_carts, orm_clear_user_cart, orm_add_purchase

pay_redsys_router = Router()

# Токен для платежного провайдера
REDSYS_TEST_PROVIDER_TOKEN = os.getenv("REDSYS_TEST_PROVIDER_TOKEN")


@pay_redsys_router.callback_query(lambda callback: callback.data == "process_order")
async def handle_process_order(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    carts = await orm_get_user_carts(session, user_id)

    description_lines = [
        f"Название: {cart.product.name} Количество: {cart.quantity} Цена: {cart.product.price * cart.quantity} USD"
        for cart in carts
    ]
    description = "\n".join(description_lines)

    total_amount_cents = int(sum(cart.product.price * cart.quantity for cart in carts) * 100)

    prices = [
        types.LabeledPrice(
            label="Ваш заказ",
            amount=total_amount_cents
        )
    ]
    
    # Отправка инвойса
    try:
        await callback.bot.send_invoice(
            chat_id=user_id,
            title="Оплата заказа",
            description=description,
            payload='Ожидайте заказ',
            provider_token=REDSYS_TEST_PROVIDER_TOKEN,
            currency="USD",
            prices=prices,
            start_parameter="payment"
        )
    except Exception as e:
        print(f"Error sending invoice: {e}")
        await callback.message.answer("Произошла ошибка при отправке инвойса.")
        return

    await callback.answer()

# Обработчик успешной оплаты
@pay_redsys_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Обработчик успешного платежа
@pay_redsys_router.message(lambda message: message.successful_payment is not None)
async def successful_payment_handler(message: Message, session: AsyncSession):
    payment_info = message.successful_payment
    user_id = message.from_user.id
    carts = await orm_get_user_carts(session, user_id)

    items = [
        {
            "product_id": cart.product.id,
            "quantity": cart.quantity,
            "price": cart.product.price,
        }
        for cart in carts
    ]

    total_amount = payment_info.total_amount / 100
    description = "\n".join(
        f"Количество: {item['quantity']}. Название: {item['product_id']}. Цена: {item['price']}"
        for item in items
    )

    await orm_add_purchase(
        session=session,
        user_id=user_id,
        total_amount=total_amount,
        currency=payment_info.currency,
        description=description,
        items=items,
    )
    await orm_clear_user_cart(session, user_id)

    await message.answer(
        text=f"Спасибо за оплату! 🎉\n"
             f"Сумма: {payment_info.total_amount / 100:.2f} {payment_info.currency}\n"
             f"Описание: {payment_info.invoice_payload}"
    )
