import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

# --- Настройки (задаются в Render -> Environment, в коде менять ничего не нужно) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@your_channel")      # например @my_channel
DOWNLOAD_LINK = os.getenv("DOWNLOAD_LINK", "https://example.com/file.zip")
PORT = int(os.getenv("PORT", "8080"))                      # Render подставляет сам

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def is_subscribed(status: str) -> bool:
    """Подписан ли пользователь: creator/administrator/member/restricted — да."""
    return status in ("creator", "administrator", "member", "restricted")


def subscribe_button() -> types.InlineKeyboardMarkup:
    """Кнопка-ссылка на канал."""
    channel = CHANNEL_ID.lstrip("@")
    return types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text="Подписаться на канал", url=f"https://t.me/{channel}")
    ]])


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
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
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


# --- Веб-сервер: нужен только для того, чтобы Render считал сервис живым ---
async def health(request: web.Request) -> web.Response:
    return web.Response(text="Bot is alive")


async def start_web_server() -> None:
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Web server started on port {PORT}")


async def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN не задан: добавьте переменную окружения BOT_TOKEN")
    await start_web_server()
    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
