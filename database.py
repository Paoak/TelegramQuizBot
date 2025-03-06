import aiosqlite
from config import DB_NAME

async def create_tables():
    """
    Создает необходимые таблицы (если их нет):
    - quiz_state: хранит текущее состояние квиза для каждого пользователя.
    - quiz_results: сохраняет последний результат прохождения квиза.
    """
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS quiz_state (
                user_id INTEGER PRIMARY KEY,
                question_index INTEGER,
                score INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                user_id INTEGER PRIMARY KEY,
                score INTEGER
            )
        ''')
        await db.commit()

async def get_quiz_state(user_id: int):
    """
    Получает текущее состояние квиза для пользователя.
    Возвращает кортеж (question_index, score).
    Если записи нет, возвращает (0, 0).
    """
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index, score FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0], row[1]
            return 0, 0

async def update_quiz_state(user_id: int, question_index: int, score: int):
    """
    Обновляет состояние квиза для пользователя.
    Если записи нет, вставляет новую; если есть – заменяет.
    """
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT OR REPLACE INTO quiz_state (user_id, question_index, score) VALUES (?, ?, ?)',
            (user_id, question_index, score)
        )
        await db.commit()

async def save_quiz_result(user_id: int, score: int):
    """
    Сохраняет (или обновляет) последний результат квиза для пользователя в таблице quiz_results.
    """
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT OR REPLACE INTO quiz_results (user_id, score) VALUES (?, ?)',
            (user_id, score)
        )
        await db.commit()

async def get_quiz_result(user_id: int) -> int:
    """
    Возвращает последний сохранённый результат квиза для пользователя.
    Если результата нет, возвращает None.
    """
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT score FROM quiz_results WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def get_statistics():
    """
    Возвращает список результатов всех пользователей в формате [(user_id, score), ...].
    """
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id, score FROM quiz_results') as cursor:
            rows = await cursor.fetchall()
            return rows

async def reset_all_quiz_states():
    """
    Сбрасывает состояние квиза для всех пользователей:
    устанавливает question_index = 0 и score = 0.
    Это используется при перезапуске бота.
    """
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE quiz_state SET question_index = 0, score = 0')
        await db.commit()

async def get_all_user_ids():
    """
    Возвращает список всех user_id, для которых есть запись в таблице quiz_state.
    Это нужно для уведомления пользователей при перезапуске бота.
    """
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id FROM quiz_state') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]