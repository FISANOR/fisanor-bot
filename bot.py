import asyncio
import logging

from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.filters import Command
from aiogram.filters import Text
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    CallbackQuery
)

API_TOKEN = "8138203975:AAE-q7SaDll1TOuFfB-inw3VsEjSowFlASM"
ADMIN_ID = 5410641725

# Каналы для подписки
CHANNELS = [
    "https://t.me/fisanor_market",
    "https://t.me/FISANOR_market_homeaccs",
    "https://t.me/FISANOR_marketplace_official"
]

CHANNEL_USERNAMES = [
    "fisanor_market",
    "FISANOR_market_homeaccs",
    "FISANOR_marketplace_official"
]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# Регистрируем router
dp.include_router(router)

# Клавиатура
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Каталог"), KeyboardButton(text="📦 Корзина")],
        [KeyboardButton(text="🚚 Доставка и оплата"), KeyboardButton(text="📞 Поддержка")],
        [KeyboardButton(text="📣 Каналы")]
    ],
    resize_keyboard=True
)

catalog_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Электроника", callback_data="cat_electronics"),
            InlineKeyboardButton(text="Косметика", callback_data="cat_cosmetics")
        ],
        [
            InlineKeyboardButton(text="Товары для дома", callback_data="cat_home")
        ]
    ]
)

# Продукты
products = {
    "cat_electronics": [
        {
            "name": "Пистолет массажёр",
            "price": 105000,
            "photo": "https://i.imgur.com/sRPfAmq.jpeg"
        },
        {
            "name": "Геймерский головной проводной наушники с RGB подсветкой",
            "price": 150000,
            "photo": "https://i.imgur.com/kP2j2NU.jpeg"  # пример, можешь поменять
        }
    ],
    "cat_cosmetics": [
        {"name": "Маска для лица", "price": 35000},
        {"name": "Мицеллярная вода", "price": 25000}
    ],
    "cat_home": [
        {"name": "Комод", "price": 4850000},
        {"name": "Этажерка для кухни", "price": 175000}
    ]
}

user_cart = {}

# Проверка подписки
async def check_subscriptions(user_id):
    for channel in CHANNEL_USERNAMES:
        chat_member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        if chat_member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return False
    return True

# /start
@router.message(F.text == "/start")
async def start_cmd(message: Message):
    user_cart[message.from_user.id] = []
    await message.answer("Добро пожаловать в FISANOR-market! Выберите действие:", reply_markup=main_kb)

# Каталог
@router.message(F.text.contains(["Каталог", "🛍 Каталог"]))
async def show_catalog(message: Message):
    if not await check_subscriptions(message.from_user.id):
        await message.answer("Пожалуйста, подпишитесь на наши каналы, чтобы просматривать каталог и получить бесплатную доставку по Узбекистану!\n\nНажмите на кнопку \"📣 Каналы\" и подпишитесь на все каналы.")
        return
    await message.answer("Выберите категорию:", reply_markup=catalog_kb)

# Кнопка "Каналы"
@router.message(F.text == "📣 Каналы")
async def show_channels(message: Message):
    text = "Подпишитесь на наши каналы, чтобы получить бесплатную доставку по Узбекистану:\n\n"
    for url in CHANNELS:
        text += f"👉 {url}\n"
    await message.answer(text)

# Показываем товары
@router.callback_query(F.data.startswith("cat_"))
async def show_products(callback: CallbackQuery):
    category = callback.data
    items = products.get(category, [])

    for item in items:
        button = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_{item['name']}")]
            ]
        )

        # Если товар — пистолет массажёр, отправляем с фото
        if item["name"] == "Пистолет массажёр":
            photo_url = "https://cdn.openai.com/chat-assets/user-uploads/file_00000000eecac86e45a5d6a6c36ddc1a.png"
            await callback.message.answer_photo(
                photo=photo_url,
                caption=f"🛒 {item['name']}\n💵 Цена: {item['price']} сум",
                reply_markup=button
            )
        else:
            # Остальные товары — текстом
            await callback.message.answer(
                f"🛒 {item['name']}\n💵 Цена: {item['price']} сум",
                reply_markup=button
            )

    await callback.answer()

# Добавление в корзину
@router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery):
    item_name = callback.data[4:]
    user_id = callback.from_user.id
    user_cart.setdefault(user_id, []).append(item_name)
    await callback.answer(f"Товар '{item_name}' добавлен в корзину!")

# Корзина
@router.message(F.text == "📦 Корзина")
async def show_cart(message: Message):
    items = user_cart.get(message.from_user.id, [])
    if not items:
        await message.answer("Ваша корзина пуста.")
        return
    cart_text = "\n".join(f"- {item}" for item in items)
    cart_text += "\n\nЧтобы оформить заказ, напишите свой адрес и имя."
    await message.answer(cart_text)

# Оплата
@router.message(F.text == "🚚 Доставка и оплата")
async def delivery_info(message: Message):
    await message.answer(
        "Вы можете выбрать доставку до дома или самовывоз по адресу: https://maps.app.goo.gl/V3MN6X1xiSPTSVEi6\n"
        "\n💳 Оплата на карту: 4023 0605 0832 1527 (Abduxakimov Xasan Botiro'vich)\n\n"
        "⏱ Срок доставки: 14–25 дней\n💰 Минимальный заказ: 140 000 сум"
    )

# Поддержка
@router.message(F.text == "📞 Поддержка")
async def support_info(message: Message):
    await message.answer(
        "По любым вопросам обращайтесь в поддержку:\n"
        "@fisanor_admin (亗.乂.丫.匚.八.|–|.亗)\n@fisanor (Xasan) — 24/7 на связи"
    )

# Заказ
@router.message()
async def handle_order(message: Message):
    items = user_cart.get(message.from_user.id, [])
    if items:
        if not await check_subscriptions(message.from_user.id):
            await message.answer("Пожалуйста, подпишитесь на все каналы, чтобы оформить заказ. Нажмите \"📣 Каналы\" и подпишитесь.")
            return

        order_text = f"🛒 Новый заказ от @{message.from_user.username or 'без ника'} (ID: {message.from_user.id}):\n"
        order_text += "\n".join(f"- {item}" for item in items)
        order_text += f"\n\n📍 Адрес: {message.text}"

        await bot.send_message(ADMIN_ID, order_text)
        await message.answer("✅ Ваш заказ отправлен! Мы свяжемся с вами в ближайшее время.")
        user_cart[message.from_user.id] = []
    else:
        await message.answer("Пожалуйста, выберите товары из каталога.")

# Запуск
async def main():
    await dp.start_polling(bot)

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running!')

def run_ping_server():
    server = HTTPServer(('0.0.0.0', 10000), PingHandler)
    server.serve_forever()

# Запускаем фейковый сервер в отдельном потоке
threading.Thread(target=run_ping_server).start()

if __name__ == "__main__":
    asyncio.run(main())