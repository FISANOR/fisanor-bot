import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    CallbackQuery
)
import logging

API_TOKEN = "8138203975:AAE-q7SaDll1TOuFfB-inw3VsEjSowFlASM"
ADMIN_ID = 5410641725

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
        [KeyboardButton(text="🚚 Доставка и оплата"), KeyboardButton(text="📞 Поддержка")]
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
        {"name": "Пистолет массажёр", "price": 450000},
        {"name": "Наушники", "price": 150000}
    ],
    "cat_cosmetics": [
        {"name": "Маска для лица", "price": 35000},
        {"name": "Мицеллярная вода", "price": 25000}
    ],
    "cat_home": [
        {"name": "Комод", "price": 850000},
        {"name": "Этажерка для кухни", "price": 175000}
    ]
}

user_cart = {}

# /start
@router.message(F.text == "/start")
async def start_cmd(message: Message):
    user_cart[message.from_user.id] = []
    await message.answer("Добро пожаловать в FISANOR-market! Выберите действие:", reply_markup=main_kb)

# Каталог
@router.message(F.text == "🛍 Каталог")
async def show_catalog(message: Message):
    await message.answer("Выберите категорию:", reply_markup=catalog_kb)

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
        await callback.message.answer(f"🛒 {item['name']}: {item['price']} сум", reply_markup=button)
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
        "\n💳 Оплата на карту: 4023 0605 0832 1527 (Abduxakimov Xasan Botiro'vich)"
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

if name == "main":
    asyncio.run(main())