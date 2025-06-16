import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.utils.token import validate_token

# Загружаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверяем валидность токена (важно для Render)
try:
    validate_token(BOT_TOKEN)
except Exception as e:
    raise ValueError("❌ BOT_TOKEN is invalid!") from e

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(commands=["start"])
async def start_command(message: Message):
    await message.answer("✅ Бот запущен и работает на Render!")

# Главная функция запуска
async def main():
    print("🚀 Бот запущен через polling...")
    await dp.start_polling(bot)

# Точка входа
if __name__ == "__main__":
    asyncio.run(main())
