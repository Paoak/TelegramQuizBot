from aiogram import types, Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Список вопросов квиза (10 вопросов)
quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': ['Язык программирования', 'Змея', 'Планета', 'Кофе'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'bool'],
        'correct_option': 0
    },
    {
        'question': 'Как называется цикл, который выполняется, пока условие истинно?',
        'options': ['while', 'for', 'do-while', 'repeat'],
        'correct_option': 0
    },
    {
        'question': 'Какая функция используется для вывода на экран в Python?',
        'options': ['print', 'echo', 'write', 'show'],
        'correct_option': 0
    },
    {
        'question': 'Что такое список (list) в Python?',
        'options': ['Изменяемая последовательность', 'Неизменяемая последовательность', 'Ключ-значение', 'Функция'],
        'correct_option': 0
    },
    {
        'question': 'Какой символ используется для комментариев в Python?',
        'options': ['#', '//', '/*', ';'],
        'correct_option': 0
    },
    {
        'question': 'Как называется функция, которая возвращает количество элементов в списке?',
        'options': ['len()', 'count()', 'size()', 'number()'],
        'correct_option': 0
    },
    {
        'question': 'Что такое словарь (dict) в Python?',
        'options': ['Набор пар ключ-значение', 'Список чисел', 'Строка', 'Кортеж'],
        'correct_option': 0
    },
    {
        'question': 'Какой метод используется для добавления элемента в список?',
        'options': ['append()', 'add()', 'insert()', 'push()'],
        'correct_option': 0
    },
    {
        'question': 'Как называется исключение, возникающее при делении на ноль?',
        'options': ['ZeroDivisionError', 'TypeError', 'ValueError', 'IndexError'],
        'correct_option': 0
    },
]

def generate_options_keyboard(answer_options):
    """
    Функция создает inline-клавиатуру с вариантами ответов.
    Для каждого варианта формируется callback_data с индексом варианта (например, "answer:0").
    """
    builder = InlineKeyboardBuilder()
    for index, option in enumerate(answer_options):
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"answer:{index}"  # передаем индекс ответа
        ))
    # Располагаем кнопки в одну строку
    builder.adjust(1)
    return builder.as_markup()
