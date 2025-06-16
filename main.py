from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    await message.answer("Бот работает!")

async def main():
    print("🚀 Polling запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
