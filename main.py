from telebot import TeleBot
from database import *
import telebot
import database
from speechkit import speech_to_text, text_to_speech
from config import *
import yandex_gpt


logging.basicConfig(filename='bot.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #Создаем бота
bot = TeleBot(TOKEN)
db = database


    #Обрабатываем команду /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    db.create_db()
    db.create_table()
    users = db.select_all_user()
    if len(users) >= MAX_USERS:
        bot.send_message(message.from_user.id, text='Количество юзеров на нашем сервисе ограничено, ты не можешь воспользоваться ботом')
        return
    bot.send_message(user_id, 'Отправь голосовое сообщение или текстовое 1 раз, чтобы я его распознал и если получил ответ можешь воспользоваться преоброзователем /stt или /tts!')
    db.add_new_user(message.from_user.id)
    bot.register_next_step_handler(message, handle_voice)


@bot.message_handler(commands=['stt'])
def start_handler(message):
    user_id = message.from_user.id
    db.create_db()
    db.create_table()
    users = db.select_all_user()
    if len(users) >= MAX_USERS:
        bot.send_message(message.from_user.id, text='Количество юзеров на нашем сервисе ограничено, ты не можешь воспользоваться ботом')
        return
    bot.send_message(user_id, 'Отправь голосовое сообщение, чтобы я его распознал!')
    db.add_new_user(message.from_user.id)
    bot.register_next_step_handler(message, handle_voicee)


@bot.message_handler(content_types=['voice'])
def handle_voicee(message: telebot.types.Message):
    user_id = message.from_user.id
    tokenss = db.get_for_user(user_id, 'total_gpt_token')
    blockss = db.get_for_user(user_id, 'total_stt_blocks')

    if tokenss >= MAX_TOKENS:
        bot.send_message(user_id, text='Израсходован лимит по токенам')
        return

    if blockss >= MAX_BLOCKS:
        bot.send_message(user_id, text='Израсходован лимит по аудио блокам')
        return

    if message.voice.duration > 15:
        bot.send_message(user_id, "Сообщение не должно быть дольше 15 секунд")
        return
    # Проверка, что сообщение действительно голосовое
    if not message.voice:
        return

    filee_id = message.voice.file_id  # получаем id голосового сообщения
    filee_info = bot.get_file(filee_id)  # получаем информацию о голосовом сообщении
    filee = bot.download_file(filee_info.file_path)  # скачиваем голосовое сообщение
    status, text = speech_to_text(filee)
    bot.send_message(message.chat.id, text)
    tokenss += len(text)
    blockss += 1
    db.update_data_of_user(user_id, 'total_gpt_token', tokenss) # обновляем информацию о токенах
    db.update_data_of_user(user_id, 'total_stt_blocks', blockss) # обновляем информацию о блоках


@bot.message_handler(commands=['tts'])
def start(message):
    db.create_db()
    db.create_table()
    bot.send_message(message.from_user.id, "Привет! Я могу озвучить текст.")
    db.delete_data(message.from_user.id)
    bot.register_next_step_handler(message, text_sp)

@bot.message_handler(content_types=['text'])
def text_sp(message):
    file = message.text
    user_id = message.from_user.id
    if len(file) > MAX_LETTERS:
        bot.send_message(user_id, "Запрос превышает количество символов\nИсправь запрос")
        bot.register_next_step_handler(message, text_sp)
        return
    db.insert_data(user_id, file, len(file))
    status, audio = text_to_speech(file)
    bot.send_audio(message.from_user.id, audio)


    #Ждем от пользователя голосовое сообщение
@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):
    user_id = message.from_user.id
    tokens = db.get_for_user(user_id, 'total_gpt_token')
    blocks = db.get_for_user(user_id, 'total_stt_blocks')

    if tokens >= MAX_TOKENS:
        bot.send_message(user_id, text='Израсходован лимит по токенам')
        return

    # Проверка, что сообщение действительно голосовое
    if not message.voice:
        file_text = message.text
        user_id = message.from_user.id
        if len(file_text) > MAX_LETTERS:
            bot.send_message(user_id, "Запрос превышает количество символов\nИсправь запрос")
            return
        db.insert_data(user_id, file_text, len(file_text))
        otvet = yandex_gpt.ask_gpt(file_text)
        bot.send_message(user_id, text=otvet)

    elif message.voice:
        if blocks >= MAX_BLOCKS:
           bot.send_message(user_id, text='Израсходован лимит по аудио блокам')
           return
        if message.voice.duration > 15:
           bot.send_message(user_id, "Сообщение не должно быть дольше 15 секунд")
           return
        file_id = message.voice.file_id  #Получаем id голосового сообщения
        file_info = bot.get_file(file_id)  #Получаем информацию о голосовом сообщении
        file = bot.download_file(file_info.file_path)  #Скачиваем голосовое сообщение
        status, text = speech_to_text(file)
        text_voi = yandex_gpt.ask_gpt(text)
        status, voi_mess = text_to_speech(text_voi)
        bot.send_audio(message.chat.id, voi_mess)
        tokens += len(text)
        blocks += 1
        db.update_data_of_user(user_id, 'total_gpt_token', tokens) #Обновляем информацию о токенах
        db.update_data_of_user(user_id, 'total_stt_blocks', blocks) #Обновляем информацию о блоках










bot.polling()  #Запускаем бота
