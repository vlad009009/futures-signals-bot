from aiogram import Bot, Dispatcher, types

BOT_TOKEN = "твой_токен_бота"  # Замени на свой реальный токен

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для сигналов по фьючерсам OKX.")

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
