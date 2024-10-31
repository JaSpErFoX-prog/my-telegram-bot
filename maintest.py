import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telethon import TelegramClient, events

# Telethon API ID и Hash
api_id = '29500030'
api_hash = '2a2ea6f8f32b60695219e464699b54fa'
phone_number = '+375333538369'

# Файл сессии Telethon
client = TelegramClient('anon', api_id, api_hash)

# Хранилище ID подписанного канала и чата для пересылки
subscribed_channel_id = None
forward_chat_id = None
bot_running = False  # Переменная для отслеживания состояния работы бота

# Чтение ID канала и чата для пересылки из файлов при старте
if os.path.exists('channel_id.txt'):
    with open('channel_id.txt', 'r') as f:
        subscribed_channel_id = int(f.read().strip())

if os.path.exists('forward_chat_id.txt'):
    with open('forward_chat_id.txt', 'r') as f:
        forward_chat_id = int(f.read().strip())

# Функция для получения ID канала через ссылку
async def get_channel_id(channel_link):
    channel = await client.get_entity(channel_link)
    return channel.id

# Функция для получения списка участников группы
async def get_group_members(chat_id):
    try:
        # Преобразуем `chat_id` в нужную сущность
        entity = await client.get_entity(chat_id)
        participants = await client.get_participants(entity)
        usernames = [f"@{p.username}" for p in participants if p.username]
        return ' '.join(usernames)
    except ValueError as e:
        print(f"Ошибка при получении участников группы: {e}")
        return ""

@client.on(events.NewMessage(chats=subscribed_channel_id))
async def handle_new_message(event):
    global forward_chat_id
    if bot_running and event.message:
        # Проверка на наличие хештегов #замена, #замены, #расписание или #звонки в тексте сообщения
        if any(hashtag in event.message.text.lower() for hashtag in ['#замена', '#замены', '#расписание', '#звонки']):
            if forward_chat_id:
                usernames = await get_group_members(forward_chat_id)
                await client.send_message(forward_chat_id, f"{usernames}\n{event.message.text}")

                # Проверка и обработка всех медиафайлов
                if event.message.grouped_id:
                    # Получаем все сообщения в альбоме
                    messages = await client.get_messages(event.chat_id, limit=100)  # Получаем последние 100 сообщений
                    for msg in messages:
                        if msg.grouped_id == event.message.grouped_id and msg.media:
                            file_path = await client.download_media(msg.media)
                            await client.send_file(forward_chat_id, file_path)
                            os.remove(file_path)
                else:
                    # Если это одно вложение, а не альбом
                    if event.message.media:
                        file_path = await client.download_media(event.message.media)
                        await client.send_file(forward_chat_id, file_path)
                        os.remove(file_path)

        # Проверка текстового сообщения на наличие группы "516"
        elif '516' in event.message.text:
            if forward_chat_id:
                usernames = await get_group_members(forward_chat_id)
                await client.send_message(forward_chat_id, f"{usernames}\n{event.message.text}")

# Команды управления ботом
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_running
    if not bot_running:
        bot_running = True
        await update.message.reply_text(f'Привет, {update.effective_user.first_name}! Бот активирован.')
        await client.start(phone=phone_number, code_callback=lambda: input('Введите код: '))
        print("Telethon клиент успешно запущен!")
    else:
        await update.message.reply_text("Бот уже активирован!")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_running
    if bot_running:
        bot_running = False
        await update.message.reply_text('Бот остановлен!')
        # Не отключаем клиент, чтобы он продолжал обрабатывать личные сообщения
    else:
        await update.message.reply_text("Бот уже остановлен!")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global subscribed_channel_id
    channel_link = update.message.text.split(maxsplit=1)[1]
    subscribed_channel_id = await get_channel_id(channel_link)
    with open('channel_id.txt', 'w') as f:
        f.write(str(subscribed_channel_id))
    await update.message.reply_text(f"Подписан на канал с ID: {subscribed_channel_id}")

async def set_forward_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global forward_chat_id
    chat_link = update.message.text.split(maxsplit=1)[1]
    forward_chat_id = await get_channel_id(chat_link)
    with open('forward_chat_id.txt', 'w') as f:
        f.write(str(forward_chat_id))
    await update.message.reply_text(f"Установлен чат для пересылки с ID: {forward_chat_id}")

# Обработка личных сообщений от пользователей
@client.on(events.NewMessage(from_users='me'))  # Измените 'me' на свой ID, если нужно
async def handle_personal_message(event):
    global bot_running
    if event.message.text.strip().lower() == "работаешь?":
        response = "Да, работаю!" if bot_running else "Нет, я не работаю!"
        await event.reply(response)

# Создание и запуск бота
app = ApplicationBuilder().token("7938740841:AAH4UX2G5308aOk2fr-IWAkc9MopCWTaGf0").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("subscribe", subscribe))
app.add_handler(CommandHandler("setforwardchat", set_forward_chat))

if __name__ == "__main__":
    app.run_polling()
