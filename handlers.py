import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from config import API_TOKEN
from quiz_data import quiz_data, generate_options_keyboard
import database

# Создаем экземпляр бота
bot = Bot(token=API_TOKEN)
# Создаем диспетчер (бот будет передаваться при старте поллинга)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Отправляет стартовое сообщение с уведомлением о перезапуске
    и выводит клавиатуру с кнопками "Начать игру" и "Статистика".
    """
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Статистика"))
    await message.answer(
        "Бот запущен. Нажмите кнопку «Начать игру» или введите /quiz для старта.",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# Обработчик команды /quiz и кнопки "Начать игру"
@dp.message(lambda message: message.text in ["Начать игру", "/quiz"])
async def cmd_quiz(message: types.Message):
    """
    Запускает квиз: отправляет приветственное сообщение и инициализирует состояние квиза.
    """
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Статистика"))
    await message.answer("Давайте начнем квиз!",
                         reply_markup=builder.as_markup(resize_keyboard=True))
    await start_quiz(message)

# Обработчик команды /stats и кнопки "Статистика"
@dp.message(lambda message: message.text in ["Статистика", "/stats"])
async def cmd_stats(message: types.Message):
    """
    Выводит последнюю сохранённую статистику прохождения квиза для пользователя.
    """
    result = await database.get_quiz_result(message.from_user.id)
    if result is not None:
        await message.answer(f"Ваш последний результат: {result} из {len(quiz_data)}")
    else:
        await message.answer("Статистика отсутствует. Сыграйте в квиз!")

async def start_quiz(message: types.Message):
    """
    Инициализирует состояние квиза для пользователя (сброс номера вопроса и счета)
    и отправляет первый вопрос.
    """
    user_id = message.from_user.id
    await database.update_quiz_state(user_id, 0, 0)
    await send_question(message, user_id)

async def send_question(message: types.Message, user_id: int):
    """
    Отправляет следующий вопрос пользователю.
    Если вопросы закончились, выводит итоговый результат и сохраняет его.
    """
    question_index, score = await database.get_quiz_state(user_id)
    if question_index < len(quiz_data):
        question = quiz_data[question_index]
        # Создаем клавиатуру с вариантами ответов
        kb = generate_options_keyboard(question['options'])
        await message.answer(question['question'], reply_markup=kb)
    else:
        await message.answer(f"Квиз завершен! Ваш результат: {score} из {len(quiz_data)}")
        await database.save_quiz_result(user_id, score)

# Обработчик нажатия на inline-кнопку с вариантом ответа
@dp.callback_query(lambda c: c.data.startswith("answer:"))
async def process_answer(callback: types.CallbackQuery):
    """
    Обрабатывает нажатие кнопки варианта ответа.
    Извлекает индекс выбранного ответа, сравнивает с правильным, отправляет результат,
    обновляет состояние квиза и переходит к следующему вопросу.
    """
    try:
        # Извлекаем индекс выбранного ответа из callback_data
        selected_index = int(callback.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await callback.answer("Неверные данные. Попробуйте снова.", show_alert=True)
        return

    user_id = callback.from_user.id
    question_index, score = await database.get_quiz_state(user_id)
    # Если квиз уже завершён, уведомляем пользователя
    if question_index >= len(quiz_data):
        await callback.answer("Квиз уже завершён.", show_alert=True)
        return

    question = quiz_data[question_index]
    correct_index = question['correct_option']
    correct_answer = question['options'][correct_index]
    selected_answer = question['options'][selected_index]

    # Удаляем inline-клавиатуру из предыдущего сообщения, чтобы исключить повторное нажатие
    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Формируем текст ответа в зависимости от правильности выбранного варианта
    if selected_index == correct_index:
        score += 1
        response_text = f"Вы выбрали: {selected_answer}\nВерно!"
    else:
        response_text = f"Вы выбрали: {selected_answer}\nНеправильно. Правильный ответ: {correct_answer}"

    # Отправляем сообщение с результатом выбора
    await callback.message.answer(response_text)

    # Обновляем состояние квиза: переходим к следующему вопросу и сохраняем новый счет
    question_index += 1
    await database.update_quiz_state(user_id, question_index, score)
    if question_index < len(quiz_data):
        await send_question(callback.message, user_id)
    else:
        await callback.message.answer(f"Квиз завершен! Ваш результат: {score} из {len(quiz_data)}")
        await database.save_quiz_result(user_id, score)

# Блокируем произвольный текстовый ввод, не относящийся к командам и кнопкам.
# Если текст не совпадает с разрешенными вариантами, ничего не делаем.
ALLOWED_TEXTS = {"/start", "/quiz", "/stats", "Начать игру", "Статистика"}
@dp.message(lambda message: message.text not in ALLOWED_TEXTS)
async def block_text_input(message: types.Message):
    # Просто игнорируем любые сообщения, не являющиеся командами или нажатием кнопок.
    return