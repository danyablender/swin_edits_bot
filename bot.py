import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

# --- НАСТРОЙКИ ---
TOKEN = "8704022676:AAF4SD3A6AhugVNCDSSMUp3PadVhDI1PEpQ" 
BUNDLE_PRICE = 175 # Цена за бандл (поменяй на 0 для теста)

# ПУТИ ТЕПЕРЬ ОТНОСИТЕЛЬНЫЕ (бот ищет файлы в своей папке)
DEMO_DIR = "edits_with_watermark"
BUNDLE_ARCHIVE = "bundle.zip" 

# Список файлов для витрины
EDITS = {
    "the boys.mp4": "Пацаны",
    "джокер.mp4": "Джокер",
    "ельмачо.mp4": "Эль Мачо",
    "куплинов.mp4": "Куплинов",
    "кфс.mp4": "КФС",
    "рик.mp4": "Рик",
    "тони старк.mp4": "Тони Старк"
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 1. Старт
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для заказов єдитов.\n\n"
        "Команды:\n"
        "/catalog - посмотреть мои работы (с водянкой)\n"
        "/buy - купить весь бандл (175⭐) без водянки"
    )

# 2. Каталог
@dp.message(Command("catalog"))
async def cmd_catalog(message: types.Message):
    keyboard = []
    items = list(EDITS.items())
    for i in range(0, len(items), 2):
        row = []
        file1, name1 = items[i]
        row.append(InlineKeyboardButton(text=name1, callback_data=f"show_{file1}"))
        if i + 1 < len(items):
            file2, name2 = items[i+1]
            row.append(InlineKeyboardButton(text=name2, callback_data=f"show_{file2}"))
        keyboard.append(row)
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer("Выбери єдит, чтобы посмотреть (с водянкой):", reply_markup=markup)

# 3. Показ демо-видео
@dp.callback_query(F.data.startswith("show_"))
async def show_edit(callback: types.CallbackQuery):
    filename = callback.data.split("show_")[1]
    filepath = os.path.join(DEMO_DIR, filename)
    
    if os.path.exists(filepath):
        video = FSInputFile(filepath)
        await callback.message.answer_video(video, caption=f"Превью: {EDITS[filename]}\n\nЧтобы купить бандл за {BUNDLE_PRICE}⭐, пиши /buy")
    else:
        await callback.message.answer(f"Файл не найден: {filename}")
    
    await callback.answer()

# 4. Покупка (выставление счета)
@dp.message(Command("buy"))
async def cmd_buy(message: types.Message):
    prices = [LabeledPrice(label="Бандл из 7 єдитов", amount=BUNDLE_PRICE)]
    
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Бандл єдитов (7 шт.)",
        description="Все 7 работ без водянки (в архиве).",
        payload="bundle_purchase",
        provider_token="", 
        currency="XTR",
        prices=prices,
        start_parameter="buy-bundle"
    )

# 5. Проверка перед оплатой
@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# 6. Выдача товара после оплаты
@dp.message(lambda message: message.successful_payment is not None)
async def process_successful_payment(message: types.Message):
    await message.answer("Оплата прошла! Лови свой бандл. 🎬")
    
    if os.path.exists(BUNDLE_ARCHIVE):
        archive = FSInputFile(BUNDLE_ARCHIVE)
        await message.answer_document(archive, caption="Твой архив с 7 єдитами. Наслаждайся.")
    else:
        await message.answer(f"Ошибка: архив не найден.\nИскал тут: {BUNDLE_ARCHIVE}\nПроверь путь.")

# Запуск
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())