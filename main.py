# -*- coding: utf-8 -*-
import os
try:
    import telebot
    import g4f.Provider
    import g4f.client
    from telebot import TeleBot, types
    import time, pathlib, sys, logging
    from MukeshAPI import api
    import g4f, random, os
    from config import *
    from qrcode import make as create_qr
    import string, requests, threading
    from gtts import gTTS
    import io
    from telebot.util import quick_markup
    from PIL import Image
except ImportError:
    input(f'Нажмите Enter для установки нужных библиотек...')
    os.system('pip install -r requirements.txt')

url = 'https://florestdev.github.io/clicker-html/'
bot = TeleBot(token=token)
path = pathlib.Path(sys.argv[0]).parent.resolve()
users = []
admins = [7455363246]

def make_black_image(message: types.Message):
    if message.document:
        if message.document.file_name[-4:] not in ['.jpg', '.png']:
            bot.reply_to(message, f'Данная функция поддерживает только `.jpg.` и `.png` файлы.', parse_mode='Markdown')
        else:
            msg = bot.reply_to(message, f'Обработка изображения, пожалуйста, подождите...')
            img = bot.download_file(bot.get_file(message.document.file_id).file_path)
            bts = io.BytesIO(img)
            bts_2 = io.BytesIO()
            #random_chislo = random.randint(1, 100)
            random_chislo_2 = random.randint(1, 200)
            #new_img_file = open(path / f'{random_chislo}.jpg', 'wb')
            #new_img_file.write(img)
            #new_img_file.close()
            with Image.open(bts) as file:
                a = file.convert('L')
                #a.save(path / f'{random_chislo_2}.jpg')
                a.save(bts_2, 'JPEG')
                bot.delete_message(message.chat.id, msg.id)
                #file = path / f'{random_chislo_2}.jpg'
                bot.send_photo(message.chat.id, bts_2.getvalue(), 'Ваше затемнное фото.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                #os.remove(file)
                #os.remove(path / f'{random_chislo}.jpg')
    elif message.photo:
            msg = bot.reply_to(message, f'Обработка изображения, пожалуйста, подождите...')
            img = bot.download_file(bot.get_file(message.photo[0].file_id).file_path)
            bts = io.BytesIO(img)
            bts_2 = io.BytesIO()
            #random_chislo = random.randint(1, 100)
            random_chislo_2 = random.randint(1, 200)
            #new_img_file = open(path / f'{random_chislo}.jpg', 'wb')
            #new_img_file.write(img)
            #new_img_file.close()
            with Image.open(bts) as file:
                a = file.convert('L')
                #a.save(path / f'{random_chislo_2}.jpg')
                a.save(bts_2, 'JPEG')
                bot.delete_message(message.chat.id, msg.id)
                #file = path / f'{random_chislo_2}.jpg'
                bot.send_photo(message.chat.id, bts_2.getvalue(), 'Ваше затемнное фото.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                #os.remove(file)
                #os.remove(path / f'{random_chislo}.jpg')
    else:
        bot.reply_to(message, f'Поддерживаются только изображения без сжатия, или с сжатием.')

def check_user(user: int):
    if str(user) in open(path / 'banned_users.txt').readlines():
        return True
    else:
        return False

def check_sub(user_id: int):
    member = bot.get_chat_member(telegram_channel_id, user_id).status
    if member in ['kicked', 'left']:
        return False
    else:
        return True

def send_reaction(chat_id: int, message_id: int, emoji: str):
    requests.post(f'https://api.telegram.org/bot{token}/setMessageReaction', json={"chat_id":chat_id, 'message_id':message_id, 'reaction':[{'type':'emoji', 'emoji':emoji}], 'is_big':False})

def download_music():
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,fi;q=0.6,nb;q=0.5,is;q=0.4,pt;q=0.3,ro;q=0.2,it;q=0.1,de;q=0.1',
        'Connection': 'keep-alive',
        'Referer': 'https://music.yandex.ru/chart',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'X-Current-UID': '403036463',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Retpath-Y': 'https://music.yandex.ru/chart',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
    }

    params = {
        'what': 'chart',
        'lang': 'ru',
        'external-domain': 'music.yandex.ru',
        'overembed': 'false',
        'ncrnd': '0.23800355071570123',
    }
    result = []
    response = requests.get('https://music.yandex.ru/handlers/main.jsx', params=params, headers=headers)
    chart = response.json()['chartPositions']
    for track in chart[:10]:
        position = track['track']['chart']['position']
        title = track['track']['title']
        author = track['track']['artists'][0]['name']
        result.append(f"№{position}: {author} - {title}")
    return f'Чарты Яндекс Музыки на данный момент🔥\n🥇{result[0]}\n🥈{result[1]}\n🥉{result[2]}\n{result[3]}\n{result[4]}\n{result[5]}\n{result[6]}\n{result[7]}\n{result[8]}\n{result[9]}'

@bot.message_handler(commands=['start'])
def welcome(message: types.Message):
    if check_sub(message.from_user.id):
        markup1 = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(f'Инфа о боте', url='https://telegra.ph/INFORMACIYA-O-BOTE-06-27')
        button21 = types.InlineKeyboardButton('Telegram канал', 'https://t.me/florestchannel')
        button31 = types.InlineKeyboardButton('Другие ресурсы Флореста', url='https://taplink.cc/florestone4185')
        markup1.add(button1, button21, button31)
        bot.send_message(message.chat.id, f'Добро пожаловать в бота Флореста.\nВсе функции находятся в меню ниже.', reply_markup=markup1)
        msg=bot.send_message(message.chat.id, f'Утилиты бота', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Погода', callback_data='weather-info'), types.InlineKeyboardButton('Разговор с ChatGPT', callback_data='ai-text'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Групповой чат [BETA]', callback_data='group-chat-beta'), types.InlineKeyboardButton('Сыграть в кликер [NEW]', web_app=types.WebAppInfo(url)), types.InlineKeyboardButton('Топ песни с чартов', callback_data='download-audio-from-youtube'), types.InlineKeyboardButton('Затемнить фотографию', callback_data='black-photo-make')))
        bot.reply_to(msg, f'На будущее, вдруг меню пропадет.', reply_markup=types.ReplyKeyboardMarkup(True).add(types.KeyboardButton('🏡В меню')))
    else:
        bot.reply_to(message, f'Ты не подписался на Telegram канал создателя?\nПора-бы это сделать!', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Мой Telegram канал', 'https://t.me/florestchannel'), types.InlineKeyboardButton('Подтвердить подписку', callback_data='check_sub')))

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
    if message.from_user.id != 7455363246:
        bot.reply_to(message, f'Ошибка! Доступ к данной панели есть только у создателя бота @florestone4185.')
    else:
        bot.reply_to(message, f'Здаров, Флорест.\nНиже кнопки действий.', protect_content=True, reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Заблокировать видео', callback_data='ban-video'), types.InlineKeyboardButton('Заблокировать канал', callback_data='ban-channel'), types.InlineKeyboardButton('Добавить Inline клавиатуру', callback_data='add_keyboard_admin_panel')))

@bot.message_handler(commands=['donate'])
def send_donate(message: types.Message):
    qr = path / 'qr-donations.jpg'
    bot.send_photo(message.chat.id, qr.open('rb'), f'Привет! Данная функция нужна для того, чтобы Вы могли отправить деньги Флоресту.\nВоспользуйтесь QR кодом выше, либо кнопками ниже.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('DonationAlerts', url='https://donationalerts.com/r/florestdev4185'), types.InlineKeyboardButton('Звезды Telegram', callback_data='tg-stars_callback'), types.InlineKeyboardButton('Криптокошелек Telegram (Ton Space)', callback_data='crypto-wallet'), types.InlineKeyboardButton('ЮMoney', callback_data='yoomoney-payment')))

@bot.message_handler(content_types=['text'])
def text_obrabbbb(message: types.Message):
    if message.text == '🏡В меню':
        if check_sub(message.from_user.id):
            bot.send_message(message.chat.id, f'Утилиты бота', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Погода', callback_data='weather-info'), types.InlineKeyboardButton('Разговор с ChatGPT', callback_data='ai-text'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Групповой чат [BETA]', callback_data='group-chat-beta'), types.InlineKeyboardButton('Сыграть в кликер [NEW]', web_app=types.WebAppInfo(url)), types.InlineKeyboardButton('Топ песни с чартов', callback_data='download-audio-from-youtube'), types.InlineKeyboardButton('Затемнить фотографию', callback_data='black-photo-make'))))
        else:
            bot.reply_to(message, f'Ты не подписался на Telegram канал создателя?\nПора-бы это сделать!', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Мой Telegram канал', 'https://t.me/florestchannel'), types.InlineKeyboardButton('Подтвердить подписку', callback_data='check_sub')))
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
        bot.edit_message_reply_markup(telegram_channel_id, int(id), reply_markup=quick_markup(eval(message.text), 1))
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
        bot.send_message(call.message.chat.id, f'Утилиты бота.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Погода', callback_data='weather-info'),  types.InlineKeyboardButton('Разговор с ChatGPT', callback_data='ai-text'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Групповой чат [BETA]', callback_data='group-chat-beta'), types.InlineKeyboardButton('Сыграть в кликер [NEW]', web_app=types.WebAppInfo(url)), types.InlineKeyboardButton('Топ песни с чартов', callback_data='download-audio-from-youtube'), types.InlineKeyboardButton('Затемнить фотографию', callback_data='black-photo-make'))))
    if call.data == 'chat_zaversit':
        bot.send_message(call.message.chat.id, f'Было приятно с Вами пообщаться! Если захотите еще, то нажмите на кнопку в команде `/start`.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
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
        bot.send_message(call.message.chat.id, f'Утилиты бота.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Погода', callback_data='weather-info'), types.InlineKeyboardButton('Разговор с ChatGPT', callback_data='ai-text'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Групповой чат [BETA]', callback_data='group-chat-beta'), types.InlineKeyboardButton('Сыграть в кликер [NEW]', web_app=types.WebAppInfo(url)), types.InlineKeyboardButton('Топ чартов', callback_data='download-audio-from-youtube'), types.InlineKeyboardButton('Затемнить фотографию', callback_data='black-photo-make'))))
    if call.data == 'help':
        bot.answer_callback_query(call.id, f'Привет!\nДля помощи по боту, Вам нужно связаться с его создателем (Флорестом).\nДержите его социальные сети!\nTelegram: @florestone4185\nDiscord: florestone4185\nE-Mail: florestone4185@internet.ru', True)
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
            bot.send_message(call.message.chat.id, f'Утилиты бота.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Погода', callback_data='weather-info'), types.InlineKeyboardButton('Разговор с ChatGPT', callback_data='ai-text'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Групповой чат [BETA]', callback_data='group-chat-beta'), types.InlineKeyboardButton('Сыграть в кликер [NEW]', web_app=types.WebAppInfo(url)), types.InlineKeyboardButton('Топ песни с чартов', callback_data='download-audio-from-youtube'), types.InlineKeyboardButton('Затемнить фотографию', callback_data='black-photo-make'))))
            users.remove(call.from_user.id)
            for __ in users:
                bot.send_message(__, f'{call.from_user.first_name} ({call.from_user.id}) покинул(а) чат. Будем его(ее) ждать вновь!')
        else:
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            bot.send_message(call.message.chat.id, f'Утилиты бота.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Погода', callback_data='weather-info'), types.InlineKeyboardButton('Разговор с ChatGPT', callback_data='ai-text'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Групповой чат [BETA]', callback_data='group-chat-beta'), types.InlineKeyboardButton('Сыграть в кликер [NEW]', web_app=types.WebAppInfo(url)), types.InlineKeyboardButton('Топ песни с чартов', callback_data='download-audio-from-youtube'), types.InlineKeyboardButton('Затемнить фотографию', callback_data='black-photo-make'))))
            users.remove(call.from_user.id)
    if call.data == 'tg-stars_callback':
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_invoice(call.message.chat.id, 'Донат Флоресту', f'Привет, тут ты можешь задонатить Флоресту 50 звезд Telegram.\nЗаранее, спасибо за потраченные звезды и время на нас!', invoice_payload='telegram-stars-payment', prices=[types.LabeledPrice('Донат Флоресту', 50)], currency='XTR', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Задонить 50 звёзд⭐', pay=True)), provider_token='')
    if call.data == 'crypto-wallet':
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, 'Мой крипто-кошелек Telegram (Ton Space, @wallet): `UQCWHkodQOQazxhCqX61pfcehapAXExrqdl9Lh5g3q9nYpJV`.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), parse_mode='Markdown')
    if call.data == 'yoomoney-payment':
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, 'Мой ЮMoney кошелек: `4100118627934427`.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), parse_mode='Markdown')
    if call.data == 'add_keyboard_admin_panel':
        bot.edit_message_text('Короч, введи ID поста для обработки.', call.message.chat.id, call.message.id, reply_markup=None)
        bot.register_next_step_handler(call.message, get_post_id)
    if call.data == 'download-audio-from-youtube':
        bot.edit_message_text(download_music(), call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    if call.data == 'check_sub':
        if check_sub(call.from_user.id):
            bot.answer_callback_query(call.id, f'Благодарим за подписку. Теперь, Вы можете начать пользоваться ботом, прописав команду /start. Приятного использования!', True)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        else:
            bot.answer_callback_query(call.id, f'Обманывать - не хорошо!', True)
    if call.data == 'correct':
        if check_sub(call.from_user.id):
            bot.answer_callback_query(call.id, 'Пожалуйста, подпишитесь на данный Telegram канал для прохождения викторины.', True)
        else:
            bot.answer_callback_query(call.id, f'Поздравляем! Вы правильно ответили на вопрос викторины.', True)
    if call.data == 'incorrect':
        if check_sub(call.from_user.id):
            bot.answer_callback_query(call.id, 'Пожалуйста, подпишитесь на данный Telegram канал для прохождения викторины.', True)
        else:
            bot.answer_callback_query(call.id, f'К сожалению, Вы проиграли. Попробуйте ввести другой вариант ответа.', True)
    if call.data == 'black-photo-make':
        bot.edit_message_text(f'Отправьте Ваше изображение (желательно формата JPG, или PNG, но лучше JPG) без сжатия (также можно и сжатием, но фотография может быть испорчена в плане качества), после завершения процесса мы Вам отправим результат.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
        bot.register_next_step_handler(call.message, make_black_image)

bot.infinity_polling(3000)
