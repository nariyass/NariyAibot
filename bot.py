import os
import base64
import tempfile
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from openai import OpenAI

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

user_photos = {}


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🧸 Привет! Я Барни — помощник NariyAiBot 💗\n\n"
        "📸 Отправь мне своё фото.\n"
        "Потом напиши, какое изображение хочешь получить.\n\n"
        "Например:\n"
        "✨ «Сделай красивую ночную фотосессию со вспышкой»\n"
        "🎀 «Сделай нежный Pinterest-образ»\n"
        "🌸 «Добавь красивый весенний фон»"
    )


@dp.message(F.photo)
async def receive_photo(message: Message):
    photo = message.photo[-1]

    file = await bot.get_file(photo.file_id)

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".jpg",
        delete=False
    )

    await bot.download_file(
        file.file_path,
        destination=temp_file.name
    )

    user_photos[message.from_user.id] = temp_file.name

    await message.answer(
        "💗 Фото получила!\n\n"
        "Теперь напиши, что хочешь сделать с ним ✨"
    )


@dp.message(F.text)
async def generate_image(message: Message):
    user_id = message.from_user.id

    if user_id not in user_photos:
        await message.answer(
            "🧸 Сначала отправь мне фотографию 📸"
        )
        return

    photo_path = user_photos[user_id]

    await message.answer(
        "✨ Барни уже творит...\n"
        "Это может занять немного времени 🧸💗"
    )

    try:
        with open(photo_path, "rb") as image_file:
            result = client.images.edit(
                model="gpt-image-2",
                image=image_file,
                prompt=message.text,
                size="1024x1024"
            )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        output_path = tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False
        ).name

        with open(output_path, "wb") as output_file:
            output_file.write(image_bytes)

        await message.answer_photo(
            photo=output_path,
            caption="✨ Готово! 🧸💗"
        )

    except Exception as error:
        print(error)

        await message.answer(
            "😔 Что-то пошло не так.\n"
            "Попробуй ещё раз через несколько секунд."
        )


async def main():
    print("🧸 NariyAiBot запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
