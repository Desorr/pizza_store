# import json
# import hashlib
# import os

# from typing import Any

# from aiohttp import ClientSession

# CRYPTOMUS_API_KEY = os.getenv("CRYPTOMUS_API_KEY")
# CRYPTOMUS_MERCHANT_ID = os.getenv("CRYPTOMUS_MERCHANT_ID")


# # Создать заголовки
# def generate_headers(data: str) -> dict[str, Any]:
#     sign = hashlib.sha256((data + CRYPTOMUS_API_KEY).encode('utf-8')).hexdigest()
#     return {"merchant": CRYPTOMUS_MERCHANT_ID, 'sign': sign, 'content-type': 'application/json'}

# # Создать инвойс
# async def create_invoice(user_id: int) -> Any:
#     async with ClientSession() as session:
#         json_dumps = json.dumps({
#             "amount": "10",
#             "order_id": f"My-Test-order-{user_id}-000",
#             "currency": "USDT",
#             "network": "tron",
#             "lifetime": 900
#         })
#         response = await session.post(
#             "https://api.cryptomus.com/v1/payment",
#             data=json_dumps,
#             headers=generate_headers(json_dumps)
#         )
#         return await response.json()
    
# # Получить инвойс
# async def get_invoice(uuid: str) -> Any:
#     async with ClientSession() as session:
#         json_dumps = json.dumps({
#             "uuid": uuid
#         })
#         response = await session.post(
#             "https://api.cryptomus.com/v1/payment/info",
#             data=json_dumps,
#             headers=generate_headers(json_dumps)
#         )
#         return await response.json()










