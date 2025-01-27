# from aiogram import F, Router, types
# from kbds.inline import MenuCallBack
# from payments.cryptomus import create_invoice, get_invoice
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from aiogram.types import CallbackQuery

# pay_router = Router()

# # Оплатить 
# @pay_router.callback_query(MenuCallBack.filter(F.menu_name == "order"))
# async def order_payment(query: CallbackQuery) -> None:
#     user_id = query.from_user.id
#     invoice = await create_invoice(user_id)
#     markup = InlineKeyboardBuilder().button(
#         text="Проверить", callback_data=f"o_{invoice['result']['uuid']}"
#     )
#     await query.message.edit_text(
#         f"Ваш счет: {invoice['result']['url']}",
#         reply_markup=markup.as_markup()
#     )

# # Проверка оплаты
# @pay_router.callback_query(F.data.startswith("o_"))
# async def check_order(query: CallbackQuery) -> None:
#     invoice = await get_invoice(query.data.split("_")[1])

#     if invoice['result']['status'] == 'paid':
#         await query.answer()
#         await query.message.answer("Счет оплачен")
#     else:
#         await query.answer("Счет не оплачен")