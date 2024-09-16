# -*- coding: utf-8 -*-
# Главный файл для работы с исходным кодом FlorestBot.
# Все переменные находятся в config.py
# Благодарю за использование данного кода!

import os # импортируем ос.

try: # пытаемся импортировать библиотеки
    import telebot
    import g4f.Provider
    import g4f.client
    from telebot import TeleBot, types
    import time, pathlib, sys, logging
    from MukeshAPI import api
    import googletrans, g4f, random, os
    from config import *
    from qrcode import make as create_qr
    import string, requests, threading
    from gtts import gTTS
    import io, pytubefix
    from telebot.util import quick_markup
except ImportError: # если их нет, то предлагаем установить зависимости из файла requirements.txt
    input(f'Внимание! Невозможно импортировать некоторые библиотеки.\nНажмите на Enter для скачивания всех нужных библиотек.')
    os.system('pip install -r requirements.txt')

url = 'https://florestdev.github.io/clicker-html/' # ссылка на кликер
bot = TeleBot(token=token) # инициализация бота
path = pathlib.Path(sys.argv[0]).parent.resolve() # узнаем точную директорию для работы с файлами
users = [] # пользователи группового чата

def check_video_url(id: str):
    file = open('prohibitions/banned_videos.txt')
    if id in file.readlines():
        return True
    else:
        return False
def check_author(author: str):
    file = open('prohibitions/banned_authors.txt')
    if author in file.readlines():
        return True
    else:
        return False

def check_user(user: int):
    if str(user) in open(path / 'banned_users.txt').readlines():
        return True
    else:
        return False

def send_reaction(chat_id: int, message_id: int, emoji: str):
    requests.post(f'https://api.telegram.org/bot{token}/setMessageReaction', json={"chat_id":chat_id, 'message_id':message_id, 'reaction':[{'type':'emoji', 'emoji':emoji}], 'is_big':False})

@bot.message_handler(commands=['start'])
def welcome(message: types.Message):
    markup1 = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(f'Инфа о боте', url='https://telegra.ph/INFORMACIYA-O-BOTE-06-27')
    button21 = types.InlineKeyboardButton('Telegram канал', 'https://t.me/florestchannel')
    button31 = types.InlineKeyboardButton('Другие ресурсы Флореста', url='https://taplink.cc/florestone4185')
    markup1.add(button1, button21, button31)
    bot.send_message(message.chat.id, f'Добро пожаловать в бота Флореста.\nВсе функции находятся в меню ниже.', reply_markup=markup1)
    msg=bot.send_message(message.chat.id, f'Утилиты бота', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Погода', callback_data='weather-info'), types.InlineKeyboardButton('Перевод текста на русский', callback_data='russian-perevod-txt'), types.InlineKeyboardButton('Разговор с ChatGPT', callback_data='ai-text'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Групповой чат [BETA]', callback_data='group-chat-beta'), types.InlineKeyboardButton('Сыграть в кликер [NEW]', web_app=types.WebAppInfo(url))))
    bot.reply_to(msg, f'На будущее, вдруг меню пропадет.', reply_markup=types.ReplyKeyboardMarkup(True).add(types.KeyboardButton('🏡В меню')))


@bot.message_handler(commands=['support'])
def support(message: types.Message):
    bot.reply_to(message, f'Связаться со мной по поводу ошибок бота, либо сотрудничества или по другим причинам.\nМоя почта: florestone4185@internet.ru\nМой Telegram аккаунт: @florestone4185\nМой Discord аккаунт: florestone4185\nЛибо нажмите кнопку ниже.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Написать на почту', 'https://inlnk.ru/oeaxRw')))

def ai_obrabotchik(message: types.Message, type: int):
    if type == 1:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        bot.send_photo(message.chat.id, api.ai_image(message.text), 'Изображение по Вашему запросу.\nМогут быть неточности. Если они присутствуют, попробуйте изменить язык на котором вы пишите запрос, или его формуляровку.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        bot.clear_step_handler_by_chat_id(message.chat.id)
    if type == 2:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
        bot.send_chat_action(message.chat.id, 'typing')
        result = g4f.client.Client().chat.completions.create(model='gpt-3.5-turbo', messages=[{"role":"user", "content":message.text}], provider=g4f.Provider.Liaobots)
        bot.reply_to(message, result.choices[0].message.content, reply_markup=markup, parse_mode='Markdown')
        bot.register_next_step_handler(message, ai_obrabotchik, 2)


@bot.message_handler(commands=['admin_panel'])
def admin_panel(message: types.Message):
    if message.from_user.id not in admins:
        bot.reply_to(message, f'Ошибка! Доступ к данной панели есть только у создателя бота.')
    else:
        bot.reply_to(message, f'Привет, {message.from_user.first_name}!', protect_content=True, reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Заблокировать видео', callback_data='ban-video'), types.InlineKeyboardButton('Заблокировать канал', callback_data='ban-channel'), types.InlineKeyboardButton('Добавить Inline клавиатуру', callback_data='add_keyboard_admin_panel')))

@bot.message_handler(commands=['donate'])
def send_donate(message: types.Message):
    qr = path / 'qr-donations.jpg'
    bot.send_photo(message.chat.id, qr.open('rb'), f'Привет! Данная функция нужна для того, чтобы Вы могли отправить деньги Флоресту.\nВоспользуйтесь QR кодом выше, либо кнопками ниже.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('DonationAlerts', url='https://donationalerts.com/r/florestdev4185'), types.InlineKeyboardButton('Звезды Telegram', callback_data='tg-stars_callback'), types.InlineKeyboardButton('Криптокошелек Tonkeeper', callback_data='crypto-wallet')))

@bot.message_handler(content_types=['text'])
def text_obrabbbb(message: types.Message):
    if message.text == '🏡В меню':
        bot.send_message(message.chat.id, f'Утилиты бота', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Погода', callback_data='weather-info'), types.InlineKeyboardButton('Перевод текста на русский', callback_data='russian-perevod-txt'), types.InlineKeyboardButton('Разговор с ChatGPT', callback_data='ai-text'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Групповой чат [BETA]', callback_data='group-chat-beta'), types.InlineKeyboardButton('Сыграть в кликер [NEW]', web_app=types.WebAppInfo(url))))
    else:
        pass

def generate_qr__(message: types.Message):
    if message.text:
        qr = create_qr(message.text)
        i1 = io.BytesIO()
        qr.save(i1, scale=10)
        qr.seek(0)
        bot.send_photo(message.chat.id, i1.getvalue(), f'Ваш QR код.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        bot.reply_to(message, f'Не смогли найти текст в Вашем сообщении.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        send_reaction(message.chat.id, message.id, '🚫')   


def get_weather(message: types.Message):
    if message.text:
        try:
            response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={message.text}&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347', headers={"User-Agent": "(Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36)"}, verify=False, proxies=proxies).text
            temperature = eval(response)['main']['temp']
            wind = eval(response)['wind']['speed']
            description = eval(response)['weather'][0]['description']
            bot.reply_to(message, f'Состояние погоды в {message.text}:\nТемпература: {temperature} °C\nВетер: {wind} м/с\nОсадки: {description}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            bot.clear_step_handler_by_chat_id(message.chat.id)
        except:
            bot.reply_to(message, f'Произошла ошибка при попытке отображения погоды.\nВы либо ввели некорректное название населенного пункта, либо API сервиса OpenWeatherMap крашнулся.\nИзвиняемся за неудобства!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
            bot.clear_step_handler_by_chat_id(message.chat.id)
            send_reaction(message.chat.id, message.id, "🤷")   
    else:
        bot.reply_to(message, f'Вы не отправили текстовое сообщение с названием Вашего города.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        send_reaction(message.chat.id, message.id, "🤷")   

def txt_document_perevod(message: types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.text:
        translated = googletrans.Translator().translate(message.text, 'ru').text
        bot.reply_to(message, translated, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        bot.reply_to(message, f'Мы не нашли текст в Вашем сообщении.')
        send_reaction(message.chat.id, message.id, "🤷")   

def create_voice_by_text(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Не смогли найти в Вашем сообщении текст.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        send_reaction(message.chat.id, message.id, "🤷")   
    else:
        try:
            bot.send_chat_action(message.chat.id, 'record_voice')
            engine = gTTS(message.text, lang='ru')
            bytes_ = io.BytesIO()
            engine.write_to_fp(bytes_)
            bot.send_audio(message.chat.id, bytes_.getvalue(), title='Из текста в аудио', performer='FlorestDev', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        except Exception as e:
            bot.reply_to(message, f'Произошла ошибка: {e}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
            send_reaction(message.chat.id, message.id, "🤷")   

def download_yt_func(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Не смогли найти текст в Вашем сообщении.')   
        send_reaction(message.chat.id, message.id, "🤷")     
    else:
        msg_repl = bot.reply_to(message, f'Видео может скачиваться небольшое количество времени. Просто, ждите.')
        try:
            send_reaction(message.chat.id, message.id, '👍')
            yt = pytubefix.YouTube(message.text, 'WEB_SAFARI', proxies=proxies)
            if yt.age_restricted:
                send_reaction(message.chat.id, message.id, "🤷")
                bot.edit_message_text(f'Невозможно скачать видео, так как на него наложены возрастные ограничения.', message.chat.id, msg_repl.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
            else:
                if check_author(yt.channel_id):
                    send_reaction(message.chat.id, message.id, "🤷")
                    bot.edit_message_text(f'Автор данного видео ({yt.author}) заблокирован в системе.\nСкачивание видео запрещено.\n(Просьба сообщать о незаконном контенте ко мне на почту. Она находится в кнопке "Помощь".)', message.chat.id, msg_repl.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
                else:
                    if check_video_url(yt.video_id):
                        send_reaction(message.chat.id, message.id, "🤷")
                        bot.edit_message_text(f'Данное видео заблокировано в системе.\nЕго скачивание запрещено.\n(Просьба сообщать о незаконном контенте ко мне на почту. Она находится в кнопке "Помощь".)', message.chat.id, msg_repl.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
                    else:
                        video = yt.streams.get_highest_resolution()
                        bytes_ = io.BytesIO()
                        video.stream_to_buffer(bytes_)
                        bot.send_chat_action(message.chat.id, 'upload_video')
                        bot.send_video(message.chat.id, bytes_.getvalue(), yt.length, caption=f'{yt.author} - {yt.title}\nПросмотры: {yt.views}\nСсылка: {message.text}\nВидео весит {len(bytes_.getvalue())} байт.', supports_streaming=True, timeout=50000, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                        bot.delete_message(message.chat.id, msg_repl.id)
        except Exception as e:
            send_reaction(message.chat.id, message.id, "🤷")
            bot.edit_message_text(f'Произошла ошибка: {e}.\nВнимание! Данная функция может не работать из-за замедления YouTube, либо из-за защиты YouTube от ботов и сторонних приложений.', message.chat.id, msg_repl.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))

def ban_video_fl(message: types.Message):
    bot.reply_to(message, f'Внесли видео в блоклист.')
    file = open('prohibitions/banned_videos.txt', 'a')
    file.write(f'\n{message.text}')
    file.close()

def ban_channel_fl(message: types.Message):
    bot.reply_to(message, f'Внесли канал в блоклист.')
    file = open('prohibitions/banned_authors.txt', 'a')
    file.write(f'\n{message.text}')
    file.close()

def add_user_to_txt(message: types.Message):
    if message.text:
        bot.reply_to(message, f'Добавляем пользователя в TXT файл.')
        with open(path / 'banned_users.txt', 'a') as file:
            file.write(f'\n{message.text}')
            file.close()
    else:
        bot.reply_to(message, f'Пользователя на базу.')

def message_hndlr(message: types.Message):
    bot.register_next_step_handler(message, message_hndlr)
    if not message.from_user.id in admins:
        if message.text:
            for _ in users:
                if _ == message.from_user.id:
                    pass
                else:
                    bot.send_message(_, f'{message.text}\n\nСообщение от {message.from_user.first_name} ({message.from_user.id})', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.voice:
            for __ in users:
                if __ == message.from_user.id:
                    pass
                else:
                    bot.send_voice(__, bot.download_file(bot.get_file(message.voice.file_id).file_path), f'Аудио от {message.from_user.first_name} ({message.from_user.id})', duration=message.voice.duration, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.contact:
            for ____ in users:
                if ____ == message.from_user.id:
                    pass
                else:
                    bot.send_message(____, f'Контакт от пользователя {message.from_user.first_name} ({message.from_user.id})')
                    bot.send_contact(____, message.contact.phone_number, message.contact.first_name, message.contact.last_name, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.sticker:
            for _____ in users:
                if _____ == message.from_user.id:
                    pass
                else:
                    bot.send_message(_____, f'Стикер от пользователя {message.from_user.first_name} ({message.from_user.id})')
                    bot.send_sticker(_____, bot.download_file(bot.get_file(message.sticker.file_id).file_path), reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')), emoji='🤖')
        elif message.photo:
            for ______ in users:
                if ______ == message.from_user.id:
                    pass
                else:
                    bot.send_photo(______, bot.download_file(bot.get_file(message.photo[0].file_id).file_path), caption=f'Фото от пользователя {message.from_user.first_name} ({message.from_user.id})', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.video_note:
            for ________ in users:
                if ________ == message.from_user.id:
                    pass
                else:
                    bot.send_message(________, f'Кружок от пользователя {message.from_user.first_name} ({message.from_user.id})')
                    bot.send_video_note(________, bot.download_file(bot.get_file(message.video_note.file_id).file_path), duration=message.video_note.duration, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.location:
            for _________ in users:
                if _________ == message.from_user.id:
                    pass
                else:
                    bot.send_message(_________, f'Локация пользователя {message.from_user.first_name} ({message.from_user.id})')
                    bot.send_location(_________, message.location.latitude, message.location.longitude, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help'))) 
        else:
            bot.reply_to(message, f'Поддерживаются только текстовые сообщение, голосовые сообщения, стикеры, кружки, фото, контакты и геолокации.')
    else:
        if message.text:
            for _ in users:
                if _ == message.from_user.id:
                    pass
                else:
                    bot.send_message(_, f'{message.text}\n\nСообщение от ADMIN`а.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.voice:
            for __ in users:
                if __ == message.from_user.id:
                    pass
                else:
                    bot.send_voice(__, bot.download_file(bot.get_file(message.voice.file_id).file_path), f'Аудио от ADMIN`a.', duration=message.voice.duration, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.contact:
            for ____ in users:
                if ____ == message.from_user.id:
                    pass
                else:
                    bot.send_message(____, f'Контакт от ADMIN`а.')
                    bot.send_contact(____, message.contact.phone_number, message.contact.first_name, message.contact.last_name, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.sticker:
            for _____ in users:
                if _____ == message.from_user.id:
                    pass
                else:
                    bot.send_message(_____, f'Стикер от ADMIN`а.')
                    bot.send_sticker(_____, bot.download_file(bot.get_file(message.sticker.file_id).file_path), reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')), emoji='🤖')
        elif message.photo:
            for ______ in users:
                if ______ == message.from_user.id:
                    pass
                else:
                    bot.send_photo(______, bot.download_file(bot.get_file(message.photo[0].file_id).file_path), caption=f'Фото от ADMIN`а.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.video_note:
            for ________ in users:
                if ________ == message.from_user.id:
                    pass
                else:
                    bot.send_message(________, f'Кружок от ADMIN`а.')
                    bot.send_video_note(________, bot.download_file(bot.get_file(message.video_note.file_id).file_path), duration=message.video_note.duration, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.location:
            for _________ in users:
                if _________ == message.from_user.id:
                    pass
                else:
                    bot.send_message(_________, f'Локация ADMIN`a.')
                    bot.send_location(_________, message.location.latitude, message.location.longitude, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help'))) 
        else:
            send_reaction(message.chat.id, message.id, "🤷")
            bot.reply_to(message, f'Поддерживаются только текстовые сообщение, голосовые сообщения, стикеры, кружки, фото, контакты и геолокации.')

@bot.pre_checkout_query_handler(lambda query: True)
def ___(pre_chekout: types.PreCheckoutQuery):
    bot.answer_pre_checkout_query(pre_chekout.id, True)

@bot.message_handler(content_types=['successful_payment'])
def success_pay(message: types.Message):
    if message.successful_payment.invoice_payload == 'telegram-stars-payment':
        bot.reply_to(message, f'Благодарим за донат в размере 50 Telegram звезд!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def add_keyboard(message: types.Message, id: str):
    try:
        bot.edit_message_reply_markup(telegram_channel_id, int(id), reply_markup=quick_markup(eval(message.text)))
        bot.reply_to(message, f'Получилось!')
    except Exception as e:
        bot.reply_to(message, f'Трабл..\n{e}')

def get_post_id(message: types.Message):
    bot.send_message(message.chat.id, f'Введи конфиг кнопки, бро.')
    bot.register_next_step_handler(message, add_keyboard, message.text)

@bot.callback_query_handler(func=lambda call: True)
def pon(call: types.CallbackQuery):
    if call.data == 'otmena_galya':
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        bot.send_message(call.message.chat.id, f'Утилиты бота.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Погода', callback_data='weather-info'), types.InlineKeyboardButton('Перевод текста на русский', callback_data='russian-perevod-txt'), types.InlineKeyboardButton('Разговор с ChatGPT', callback_data='ai-text'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Групповой чат [BETA]', callback_data='group-chat-beta'), types.InlineKeyboardButton('Сыграть в кликер [NEW]', web_app=types.WebAppInfo(url))))
    if call.data == 'chat_zaversit':
        bot.send_message(call.message.chat.id, f'Было приятно с Вами пообщаться! Если захотите еще, то нажмите на кнопку в команде `/start`.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
    if call.data == 'fact-about-cat':
        bot.edit_message_text(googletrans.Translator().translate(eval(requests.get('https://catfact.ninja/fact').text)['fact'], 'ru').text, call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    if call.data == 'generate_qr':
        bot.edit_message_text('Напиши ссылку, на которую будет вести QR код.\nИли контент, который будет показываться после сканирования.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
        bot.register_next_step_handler(call.message, generate_qr__)
    if call.data == 'generate_password':
        symbols = list(string.ascii_letters + string.digits)
        random.shuffle(symbols)
        password = ''.join(symbols[:15])
        random_symbols = ['!', '*', '$', '#', '@']
        psw = password + random.choice(random_symbols)
        bot.edit_message_text(psw, call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    if call.data == 'weather-info':
        bot.edit_message_text('Напиши название своего населенного пункта.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
        bot.register_next_step_handler(call.message, get_weather)
    if call.data == 'russian-perevod-txt':
        bot.edit_message_text(f'Пришлите ваш текст на иностранном языке для перевода на русский язык.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
        bot.register_next_step_handler(call.message, txt_document_perevod)
    if call.data == 'ai-text':
        bot.edit_message_text(f'Напишите запрос для ChatGPT, пожалуйста.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
        bot.register_next_step_handler(call.message, ai_obrabotchik, 2)
    if call.data == 'ai-image':
        bot.edit_message_text(f'Напишите текст, на основе которого мы нарисуем изображение.\nРекомендуется писать запрос на английском языке.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
        bot.register_next_step_handler(call.message, ai_obrabotchik, 1)
    if call.data == 'text-to-speech':
        bot.edit_message_text(f'Напишите текст, который нужно озвучить, пожалуйста (на русском языке).', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
        bot.register_next_step_handler(call.message, create_voice_by_text)
    if call.data == 'back':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.send_message(call.message.chat.id, f'Утилиты бота.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Погода', callback_data='weather-info'), types.InlineKeyboardButton('Перевод текста на русский', callback_data='russian-perevod-txt'), types.InlineKeyboardButton('Разговор с ChatGPT', callback_data='ai-text'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Групповой чат [BETA]', callback_data='group-chat-beta'), types.InlineKeyboardButton('Сыграть в кликер [NEW]', web_app=types.WebAppInfo(url))))
    if call.data == 'help':
        bot.answer_callback_query(call.id, f'Привет!\nДля помощи по боту, Вам нужно связаться с его создателем (Флорестом).\nДержите его социальные сети!\nTelegram: @florestone4185\nDiscord: florestone4185\nE-Mail: florestone4185@internet.ru', True)
    if call.data == 'youtube-download':
        bot.edit_message_text(f'Введите ссылку на видео, пожалуйста.\n(Не советуем скачивать какие-то длинные видео.)', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
        bot.register_next_step_handler(call.message, download_yt_func)
    if call.data == 'ban-video':
        bot.edit_message_text(f'Введи ID видео.', call.message.chat.id, call.message.id)
        bot.register_next_step_handler(call.message, ban_video_fl)
    if call.data == 'ban-channel':
        bot.edit_message_text(f'Введи ID канала.', call.message.chat.id, call.message.id)
        bot.register_next_step_handler(call.message, ban_channel_fl)
    if call.data == 'add-user-to-txt':
        bot.edit_message_text('Введи пользователя, которого нужно добавить.', call.message.chat.id, call.message.id)
        bot.register_next_step_handler(call.message, add_user_to_txt)
    if call.data == 'group-chat-beta':
        if not check_user(call.from_user.id):
            if not call.from_user.id in admins:
                users.append(call.from_user.id)
                bot.edit_message_text(f'Добро пожаловать в чат!\nНапишите свое первое сообщение в чат.\nНа данный момент находятся в чате: {str(len(users))}', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya_chat')))
                bot.register_next_step_handler(call.message, message_hndlr)
                for _ in users:
                    bot.send_message(_, f'Новый участник чата - {call.from_user.first_name} ({call.from_user.id})!')
            else:
                users.append(call.from_user.id)
                bot.edit_message_text(f'Добро пожаловать в чат!\nНапишите свое первое сообщение в чат.\nНа данный момент находятся в чате: {str(len(users))}', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya_chat')))
                bot.register_next_step_handler(call.message, message_hndlr)
        else:
            send_reaction(call.message.chat.id, call.message.id, "🤷")
            bot.edit_message_text(f'Вы были заблокированы в чате.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
    if call.data == 'otmena_galya_chat':
        if not call.from_user.id in admins:
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            bot.send_message(call.message.chat.id, f'Утилиты бота.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Погода', callback_data='weather-info'), types.InlineKeyboardButton('Перевод текста на русский', callback_data='russian-perevod-txt'), types.InlineKeyboardButton('Разговор с ChatGPT', callback_data='ai-text'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Групповой чат [BETA]', callback_data='group-chat-beta'), types.InlineKeyboardButton('Сыграть в кликер [NEW]', web_app=types.WebAppInfo(url))))
            users.remove(call.from_user.id)
            for __ in users:
                bot.send_message(__, f'{call.from_user.first_name} ({call.from_user.id}) покинул(а) чат. Будем его(ее) ждать вновь!')
        else:
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            bot.send_message(call.message.chat.id, f'Утилиты бота.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Погода', callback_data='weather-info'), types.InlineKeyboardButton('Перевод текста на русский', callback_data='russian-perevod-txt'), types.InlineKeyboardButton('Разговор с ChatGPT', callback_data='ai-text'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Групповой чат [BETA]', callback_data='group-chat-beta'), types.InlineKeyboardButton('Сыграть в кликер [NEW]', web_app=types.WebAppInfo(url))))
            users.remove(call.from_user.id)
    if call.data == 'tg-stars_callback':
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_invoice(call.message.chat.id, 'Донат Флоресту', f'Привет, тут ты можешь задонатить Флоресту 50 звезд Telegram.\nЗаранее, спасибо за потраченные звезды и время на нас!', invoice_payload='telegram-stars-payment', prices=[types.LabeledPrice('Донат Флоресту', 50)], currency='XTR', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Задонить 50 звёзд⭐', pay=True)), provider_token='')
    if call.data == 'crypto-wallet':
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, 'Мой крипто-кошелек Tonkeeper: `your-ton-keeper-wallet`.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), parse_mode='Markdown')
    if call.data == 'add_keyboard_admin_panel':
        bot.edit_message_text('Короч, введи ID поста для обработки.', call.message.chat.id, call.message.id, reply_markup=None)
        bot.register_next_step_handler(call.message, get_post_id)

bot.infinity_polling(3000)