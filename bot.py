import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# --- Настройки (задаются на хостинге, в коде менять ничего не нужно) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВСТАВЬТЕ_ТОКЕН_СЮДА")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@ваш_канал")          # например @my_channel
DOWNLOAD_LINK = os.getenv("DOWNLOAD_LINK", "https://example.com/file.zip")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def is_subscribed(status: str) -> bool:
    """Подписан ли пользователь: creator/administrator/member/restricted — да."""
    return status in ("creator", "administrator", "member", "restricted")


def subscribe_button() -> types.InlineKeyboardMarkup:
    """Кнопка-ссылка на канал."""
    channel = CHANNEL_ID.lstrip("@")
    kb = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text="Подписаться на канал", url=f"https://t.me/{channel}")
    ]])
    return kb


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! Чтобы получить файл, подпишитесь на наш канал, "
        "а затем нажмите /getfile.",
        reply_markup=subscribe_button(),
    )


@dp.message(Command("getfile"))
async def get_file(message: types.Message):
    try:
        member = await bot.get_chat_member(
            chat_id=CHANNEL_ID, user_id=message.from_user.id
        )
    except Exception:
        await message.answer(
            "Не удалось проверить подписку. Убедитесь, что бот добавлен "
            "в канал администратором."
        )
        return

    if is_subscribed(member.status):
        await message.answer(f"Спасибо за подписку! Скачать файл: {DOWNLOAD_LINK}")
    else:
        await message.answer(
            "Вы ещё не подписаны на канал. Подпишитесь и нажмите /getfile снова.",
            reply_markup=subscribe_button(),
        )


async def main():
    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
