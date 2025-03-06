import asyncio
import logging
from handlers import dp, bot
import database
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest  # Исправленный импорт

# Настройка логирования для отслеживания событий бота
logging.basicConfig(level=logging.INFO)

async def notify_users_restart():
    """
    Отправляет уведомление всем пользователям (из базы данных), что бот был перезапущен.
    При ошибках (например, если бот не может отправить сообщение конкретному пользователю)
    выводит сообщение об ошибке в лог.
    """
    user_ids = await database.get_all_user_ids()
    for user_id in user_ids:
        try:
            await bot.send_message(
                user_id,
                "Бот был перезапущен. Введите /start или введите /quiz и начните квиз."
            )
        except (TelegramForbiddenError, TelegramBadRequest) as e:
            logging.error(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")

async def main():
    """
    Главная функция, которая:
    - Создает таблицы в базе данных.
    - Сбрасывает состояния квиза для всех пользователей.
    - Уведомляет пользователей о перезапуске.
    - Запускает процесс поллинга новых обновлений от Telegram,
      игнорируя накопленные обновления (skip_updates=True).
    """
    await database.create_tables()
    await database.reset_all_quiz_states()
    await notify_users_restart()
    await dp.start_polling(bot, skip_updates=True)  # skip_updates=True предотвращает обработку накопившихся обновлений

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Во время работы произошла ошибка")
        print(f"Во время работы произошла ошибка: {e}")