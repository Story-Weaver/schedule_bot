import asyncpg
import asyncio
from datetime import datetime, timedelta

async def connect_to_postgres():
    """Устанавливает асинхронное подключение к PostgreSQL без пароля"""
    try:
        # Подключение к базе данных без пароля
        connection = await asyncpg.connect(
            host='127.0.0.1',      # Адрес сервера PostgreSQL
            port=5432,             # Порт (по умолчанию 5432)
            database='rasp',       # Имя базы данных
            user='postgres',       # Имя пользователя
            password=None          # Без пароля
        )
        
        print("Успешное подключение к PostgreSQL")
        return connection
        
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        raise

async def createPair():
    conn = await connect_to_postgres()
    try:
        await conn.fetch(f'')

    finally:
        await conn.close()


async def getDay(user_id, date):
    group_number = await getGroup(user_id)
    if group_number is None:
        return None

    conn = await connect_to_postgres()

    try:
        print(f"SELECT * FROM schedule WHERE group_number = {group_number} AND date = '{date}';")
        day = await conn.fetch(f"SELECT * FROM schedule WHERE group_number = {group_number} AND date = '{date}';")
        return day
    finally:
        await conn.close()


async def getGroup(tg_id):
    conn = await connect_to_postgres()
    try:
        group = await conn.fetchval('SELECT group_number FROM users WHERE tg_user_id = $1;', tg_id)
        return group
    
    finally:
        await conn.close()

async def add_user(tg_user_id: int, group_number: int, time: int, count: int):
    conn = await connect_to_postgres()
    try:
        await conn.execute('''
            INSERT INTO users (tg_user_id, group_number, time, count)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (tg_user_id) 
            DO UPDATE SET group_number = EXCLUDED.group_number, time = EXCLUDED.time
        ''', tg_user_id, group_number, time, count)
    finally:
        await conn.close()

async def check_user_exists(user_id) -> bool:
    try:
        conn = await connect_to_postgres()
        if conn is None:
            print("Не удалось подключиться к PostgreSQL")
            return False
            
        exists = await conn.fetchval(
            'SELECT EXISTS(SELECT 1 FROM users WHERE tg_user_id = $1)',
            user_id
        )
        return bool(exists)
    except Exception as e:
        print(f"Ошибка при проверке пользователя: {e}")
        return False
    finally:
        if conn is not None:
            await conn.close()


async def update_user_group(user_id, new_group: int) -> bool:
    conn = await connect_to_postgres()
    try:
        result = await conn.execute('UPDATE users SET group_number = $1 WHERE tg_user_id = $2;',new_group, user_id)
        if result and result.startswith('UPDATE '):
            updated_count = int(result.split()[1])
            return updated_count > 0
        return False
        
    except Exception as e:
        print(f"Ошибка при обновлении группы пользователя: {e}")
        return False
    finally:
        await conn.close()